#!/usr/bin/env python3
import argparse
import sys
import time
from urllib.parse import urlparse

try:
    from soco import SoCo
    from soco.exceptions import SoCoException
except ImportError:
    print("SoCo is required. Install with: pip install soco", file=sys.stderr)
    sys.exit(1)


def validate_url(u: str) -> None:
    p = urlparse(u)
    if p.scheme not in ("http", "https"):
        raise ValueError("URL must start with http:// or https://")
    if not p.netloc:
        raise ValueError("URL has no host")


def main():
    ap = argparse.ArgumentParser(
        description="Play an audio URL on a Sonos speaker."
    )
    ap.add_argument("--ip", required=True, help="Speaker IP (e.g. 192.168.1.18)")
    ap.add_argument("--url", required=True, help="Audio URL to play")
    ap.add_argument("--volume", type=int, default=None, help="Set volume 0..100 (optional)")
    ap.add_argument("--force", action="store_true", help="Stop current playback before play_uri")
    args = ap.parse_args()

    try:
        validate_url(args.url)
    except Exception as e:
        print(f"Bad URL: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        speaker = SoCo(args.ip)
        info = speaker.get_speaker_info()  # sanity check / wake
    except Exception as e:
        print(f"Cannot connect to speaker at {args.ip}: {e}", file=sys.stderr)
        sys.exit(3)

    room = info.get("zone_name", "?")
    model = info.get("model_name", "?")
    print(f"[*] Connected to {room} ({model}) at {args.ip}")

    try:
        if args.force:
            # Останавливаем любое текущее воспроизведение/радио/очередь
            try:
                speaker.stop()
            except SoCoException:
                pass

        if args.volume is not None:
            v = max(0, min(100, args.volume))
            speaker.volume = v
            print(f"[*] Volume set to {v}")

        # Воспроизведение прямого URI:
        # Для радио-стримов этого обычно достаточно.
        # Для файлов можно добавить title/metadata при желании.
        speaker.play_uri(args.url)
        print(f"[*] play_uri: {args.url}")

        # Небольшое ожидание и проверка состояния
        for _ in range(10):
            time.sleep(0.5)
            state = speaker.get_current_transport_info().get("current_transport_state")
            if state in ("PLAYING", "TRANSITIONING"):
                print(f"[+] State: {state}")
                break
        else:
            print("[!] Playback state did not switch to PLAYING (check the URL/format).")

    except SoCoException as e:
        print(f"Sonos error: {e}", file=sys.stderr)
        sys.exit(4)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(5)


if __name__ == "__main__":
    main()
