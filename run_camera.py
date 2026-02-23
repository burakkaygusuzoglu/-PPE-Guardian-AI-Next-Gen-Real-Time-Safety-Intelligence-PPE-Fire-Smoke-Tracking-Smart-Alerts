import cv2
import time
import csv
from pathlib import Path
from ultralytics import YOLO

# ✅ core/ppe_timer.py içinden import
from core.ppe_timer import PPEViolationTracker


# =======================
# AYARLAR
# =======================
MODEL_PATH = r"C:\Users\asus\yolov5\runs\detect\train\weights\best.pt"
CAM_ID = 0
IMG_SIZE = 640
CONF = 0.45
IOU = 0.50

# İhlal süre mantığı (ID bazlı)
VIOLATION_SECONDS_REQUIRED = 3.0

# Alarm spam engeli / foto kaydı cooldown
ALARM_COOLDOWN_SEC = 2.0

# Kayıt ayarları
SAVE_VIDEO = True
VIDEO_FPS = 30.0
SAVE_ALERT_FRAMES = True

# Çıktı klasörleri
OUT_DIR = Path(r"C:\Users\asus\Desktop\MASTER_MERGED")
REC_DIR = OUT_DIR / "recordings"
ALERT_DIR = OUT_DIR / "alerts"
REC_DIR.mkdir(parents=True, exist_ok=True)
ALERT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = ALERT_DIR / "alerts_log.csv"
if not LOG_PATH.exists():
    with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time", "level", "message", "counts", "image_path"])

# Class renkleri (BGR)
COLOR_MAP = {
    "helmet":   (255, 200,  50),
    "vest":     ( 50, 255, 255),
    "person":   (255, 255, 255),
    "fire":     (  0,   0, 255),
    "smoke":    (180, 180, 180),
    "gloves":   (255,   0, 255),
    "forklift": (  0, 165, 255),
    "goggles":  ( 50, 255,  50),
}

# =======================
# Mini IoU Tracker (Ultralytics tracker yok!)
# =======================
class SimpleTrack:
    def __init__(self, tid, box, t):
        self.id = tid
        self.box = box
        self.last_seen = t
        self.miss = 0

def iou_xyxy(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    iw = max(0.0, inter_x2 - inter_x1)
    ih = max(0.0, inter_y2 - inter_y1)
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter + 1e-9
    return inter / union

class IoUTracker:
    def __init__(self, iou_thr=0.25, max_miss=30):
        self.iou_thr = iou_thr
        self.max_miss = max_miss
        self.tracks = []
        self.next_id = 1

    def update(self, det_boxes, t):
        """
        det_boxes: list of (x1,y1,x2,y2) for PERSON only
        returns: list of (box, track_id)
        """
        matches = [-1] * len(det_boxes)
        used_tracks = set()

        for di, dbox in enumerate(det_boxes):
            best_iou = 0.0
            best_ti = -1
            for ti, tr in enumerate(self.tracks):
                if ti in used_tracks:
                    continue
                val = iou_xyxy(dbox, tr.box)
                if val > best_iou:
                    best_iou = val
                    best_ti = ti
            if best_ti >= 0 and best_iou >= self.iou_thr:
                matches[di] = best_ti
                used_tracks.add(best_ti)

        for tr in self.tracks:
            tr.miss += 1

        out = []
        for di, dbox in enumerate(det_boxes):
            ti = matches[di]
            if ti == -1:
                tid = self.next_id
                self.next_id += 1
                self.tracks.append(SimpleTrack(tid, dbox, t))
                out.append((dbox, tid))
            else:
                tr = self.tracks[ti]
                tr.box = dbox
                tr.last_seen = t
                tr.miss = 0
                out.append((dbox, tr.id))

        self.tracks = [tr for tr in self.tracks if tr.miss <= self.max_miss]
        return out

# =======================
# Yardımcılar
# =======================
def now_stamp():
    return time.strftime("%Y%m%d_%H%M%S")

def draw_box(img, box, label, color, thickness=2):
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    y_text = max(0, y1 - th - 10)
    cv2.rectangle(img, (x1, y_text), (x1 + tw + 8, y_text + th + 10), color, -1)
    cv2.putText(img, label, (x1 + 4, y_text + th + 3),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

def split_person_regions(pbox):
    x1, y1, x2, y2 = pbox
    h = (y2 - y1)
    head = (x1, y1, x2, y1 + 0.35 * h)
    torso = (x1, y1 + 0.20 * h, x2, y1 + 0.65 * h)
    return head, torso

def box_in_region(obj_box, region_box, min_iou=0.01):
    return iou_xyxy(obj_box, region_box) > min_iou

def open_writer(path: Path, w: int, h: int, fps: float):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    return cv2.VideoWriter(str(path), fourcc, fps, (w, h))


# =======================
# MAIN
# =======================
def main():
    model = YOLO(MODEL_PATH)
    tracker = IoUTracker(iou_thr=0.25, max_miss=45)

    # ✅ Profesyonel PPE süre takip sistemi (ID bazlı)
    ppe_tracker = PPEViolationTracker(
        rules_seconds={
            "no_helmet": VIOLATION_SECONDS_REQUIRED,
            "no_vest": VIOLATION_SECONDS_REQUIRED,
        },
        forget_after_sec=2.0
    )

    last_alarm_time = 0.0

    cap = cv2.VideoCapture(CAM_ID, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Kamera açılamadı. CAM_ID değiştir veya Windows izinlerini kontrol et.")
        return

    ok, frame = cap.read()
    if not ok:
        print("İlk frame okunamadı.")
        cap.release()
        return

    H, W = frame.shape[:2]

    # Video record
    recording = SAVE_VIDEO
    writer = None
    if recording:
        out_path = REC_DIR / f"record_{now_stamp()}.mp4"
        writer = open_writer(out_path, W, H, VIDEO_FPS)
        print(f"[REC] Video kaydı başladı: {out_path}")

    print("Çıkış: Q | Kayıt aç/kapat: R")

    prev_t = time.time()
    fps_smooth = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Frame okunamadı.")
            break

        tnow = time.time()
        dt = max(1e-6, tnow - prev_t)
        prev_t = tnow
        fps = 1.0 / dt
        fps_smooth = fps_smooth * 0.9 + fps * 0.1 if fps_smooth > 0 else fps

        # ========= YOLO Predict =========
        res = model.predict(source=frame, imgsz=IMG_SIZE, conf=CONF, iou=IOU, verbose=False)[0]

        # Ayrıştır
        person_boxes = []
        helmets, vests, fires, smokes, gloves, forklifts, goggles = [], [], [], [], [], [], []

        for b in res.boxes:
            cls_id = int(b.cls.item())
            confv = float(b.conf.item())
            name = res.names.get(cls_id, str(cls_id))
            x1, y1, x2, y2 = b.xyxy[0].tolist()
            box = (x1, y1, x2, y2)

            if name == "person":
                person_boxes.append(box)
            elif name == "helmet":
                helmets.append(box)
            elif name == "vest":
                vests.append(box)
            elif name == "fire":
                fires.append(box)
            elif name == "smoke":
                smokes.append(box)
            elif name == "gloves":
                gloves.append(box)
            elif name == "forklift":
                forklifts.append(box)
            elif name == "goggles":
                goggles.append(box)

            # ham det çiz
            color = COLOR_MAP.get(name, (0, 255, 0))
            draw_box(frame, box, f"{name} {confv:.2f}", color)

        # ========= ID ata =========
        people = tracker.update(person_boxes, tnow)  # list of (box, id)

        # ========= PPE Compliance (ID bazlı 3sn rule) =========
        violations_now = []   # "NO_HELMET", "NO_VEST"
        violated_ids = []     # ihlal eden pid listesi

        # ✅ tracker'ın event listesi (ID bazlı)
        for pbox, pid in people:
            head, torso = split_person_regions(pbox)

            has_helmet = any(box_in_region(h, head, min_iou=0.01) for h in helmets)
            has_vest   = any(box_in_region(v, torso, min_iou=0.01) for v in vests)

            # ✅ violations dict (tracker input)
            viol = {
                "no_helmet": (not has_helmet),
                "no_vest": (not has_vest),
            }

            events = ppe_tracker.update_person(pid, tnow, viol)

            # ID label
            draw_box(frame, pbox, f"person ID:{pid}", (255, 255, 255), thickness=2)

            # event olduysa ekranda göster
            for ev_pid, rule, dur in events:
                if rule == "no_helmet":
                    violations_now.append("NO_HELMET")
                    violated_ids.append(ev_pid)
                    draw_box(frame, pbox, f"ID:{ev_pid} NO_HELMET {dur:.1f}s", (0, 165, 255), 3)

                if rule == "no_vest":
                    violations_now.append("NO_VEST")
                    violated_ids.append(ev_pid)
                    draw_box(frame, pbox, f"ID:{ev_pid} NO_VEST {dur:.1f}s", (0, 165, 255), 3)

        # ✅ görünmeyen id’leri temizle
        ppe_tracker.cleanup(tnow)

        # ========= Alarm Kuralları =========
        has_fire_or_smoke = (len(fires) > 0) or (len(smokes) > 0)
        alarm_text = None
        alarm_level = None

        if has_fire_or_smoke:
            alarm_text = "CRITICAL: FIRE/SMOKE DETECTED!"
            alarm_level = "CRITICAL"
        elif len(violations_now) > 0:
            alarm_text = f"WARNING: {', '.join(sorted(set(violations_now)))}  IDs:{sorted(set(violated_ids))}"
            alarm_level = "WARNING"

        saved_path = ""
        if alarm_text:
            bar_color = (0, 0, 255) if alarm_level == "CRITICAL" else (0, 165, 255)
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 60), bar_color, -1)
            cv2.putText(frame, alarm_text, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 3)

            # ✅ Foto + CSV log cooldown
            if SAVE_ALERT_FRAMES and (tnow - last_alarm_time > ALARM_COOLDOWN_SEC):
                last_alarm_time = tnow
                fname = ALERT_DIR / f"alert_{alarm_level.lower()}_{now_stamp()}.jpg"
                cv2.imwrite(str(fname), frame)
                saved_path = str(fname)
                print(f"[ALERT] Kaydedildi: {fname}")

                counts = {
                    "person": len(people),
                    "helmet": len(helmets),
                    "vest": len(vests),
                    "fire": len(fires),
                    "smoke": len(smokes),
                    "gloves": len(gloves),
                    "forklift": len(forklifts),
                    "goggles": len(goggles),
                }
                with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow([now_stamp(), alarm_level, alarm_text, str(counts), saved_path])

        # Alt bilgi
        info = f"FPS:{fps_smooth:.1f} conf={CONF} imgsz={IMG_SIZE} persons={len(people)} rec={'ON' if recording else 'OFF'}"
        cv2.putText(frame, info, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Video kaydı
        if recording and writer is not None:
            writer.write(frame)

        cv2.imshow("PPE Safety AI - Live (Pro Timer)", frame)
        k = cv2.waitKey(1) & 0xFF

        if k == ord("q"):
            break
        if k == ord("r"):
            recording = not recording
            if recording and writer is None:
                out_path = REC_DIR / f"record_{now_stamp()}.mp4"
                writer = open_writer(out_path, W, H, VIDEO_FPS)
                print(f"[REC] Video kaydı başladı: {out_path}")
            elif (not recording) and writer is not None:
                writer.release()
                writer = None
                print("[REC] Video kaydı durduruldu.")

    if writer is not None:
        writer.release()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
