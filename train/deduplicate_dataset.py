import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image
import numpy as np


def dhash(image: Image.Image, hash_size: int = 8) -> str:
    image = image.convert("L").resize((hash_size + 1, hash_size), Image.LANCZOS)
    pixels = np.array(image, dtype=np.uint8)
    diff = pixels[:, 1:] > pixels[:, :-1]
    return "".join(str(int(b)) for b in diff.flatten())


def compute_hash(img_path: Path) -> Tuple[Path, str]:
    try:
        img = Image.open(img_path)
        h = dhash(img)
        img.close()
        return (img_path, h)
    except Exception:
        return (img_path, "")


def hamming_distance(h1: str, h2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(h1, h2))


def find_duplicates_fast(image_dir: Path, threshold: int = 6, workers: int = 8):
    ext_set = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    img_paths = sorted([
        p for p in image_dir.iterdir() if p.suffix.lower() in ext_set
    ])
    total = len(img_paths)
    print(f"  Total images: {total}")

    # Step 1: parallel hash computation
    print(f"  Computing hashes ({workers} threads)...")
    t0 = time.time()
    hashes: Dict[Path, str] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(compute_hash, p): p for p in img_paths}
        done = 0
        for f in as_completed(futures):
            path, h = f.result()
            if h:
                hashes[path] = h
            done += 1
            if done % 500 == 0 or done == total:
                print(f"    {done}/{total} ({done*100//total}%)")
    t1 = time.time()
    print(f"  Hash computation done in {t1-t0:.1f}s")

    valid = len(hashes)
    if valid == 0:
        return [], {}

    # Step 2: bucket by prefix bits to avoid O(n^2)
    # group by first 20 bits of hash
    prefix_len = 20
    buckets: Dict[str, List[Tuple[Path, str]]] = {}
    for path, h in hashes.items():
        key = h[:prefix_len]
        buckets.setdefault(key, []).append((path, h))

    print(f"  Buckets: {len(buckets)}, avg size: {valid/len(buckets):.1f}")

    # Step 3: compare within each bucket
    visited = set()
    groups = []
    comparisons = 0

    for bucket in buckets.values():
        for i, (p1, h1) in enumerate(bucket):
            if p1 in visited:
                continue
            group = [p1]
            visited.add(p1)
            for j in range(i + 1, len(bucket)):
                p2, h2 = bucket[j]
                if p2 in visited:
                    continue
                comparisons += 1
                if hamming_distance(h1, h2) <= threshold:
                    group.append(p2)
                    visited.add(p2)
            groups.append(group)

    print(f"  Comparisons: {comparisons} (vs O(n^2)={valid*valid//2})")

    to_remove = []
    group_details = {}
    for group in groups:
        if len(group) <= 1:
            continue
        to_remove.extend(group[1:])
        group_details[group[0].name] = group[1:]

    return to_remove, group_details


def main():
    parser = argparse.ArgumentParser(description="Dataset deduplication using dHash")
    parser.add_argument("--src", required=True, help="Dataset root")
    parser.add_argument("--threshold", type=int, default=6, help="Hamming distance threshold")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--workers", type=int, default=8, help="Thread count")
    args = parser.parse_args()

    src = Path(args.src)
    splits = ["train", "val"]
    ext_set = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    total_removed = 0
    total_origin = 0

    for split in splits:
        img_dir = src / "images" / split
        lab_dir = src / "labels" / split

        if not img_dir.exists():
            print(f"[SKIP] {img_dir} not found")
            continue

        total_origin += len([f for f in img_dir.iterdir() if f.suffix.lower() in ext_set])

        print(f"\n{'=' * 50}")
        print(f"Processing {split}")
        print(f"{'=' * 50}")

        to_remove, groups = find_duplicates_fast(
            img_dir, threshold=args.threshold, workers=args.workers
        )

        print(f"  Similar groups: {len(groups)}, duplicates to remove: {len(to_remove)}")

        if groups:
            print(f"\n  Group details (first 10):")
            for keep_name, dup_list in list(groups.items())[:10]:
                print(f"    [KEEP] {keep_name}")
                for dup in dup_list[:3]:
                    print(f"      [DEL] {dup.name}")
                if len(dup_list) > 3:
                    print(f"      ... and {len(dup_list) - 3} more")

        if args.dry_run:
            print(f"\n  [DRY-RUN] Would delete {len(to_remove)} images + labels")
            total_removed += len(to_remove)
            continue

        removed = 0
        for img_path in to_remove:
            img_path.unlink()
            label_path = lab_dir / f"{img_path.stem}.txt"
            if label_path.exists():
                label_path.unlink()
            removed += 1

        print(f"  Deleted {removed} images + labels")
        total_removed += removed

    print(f"\n{'=' * 50}")
    print(f"Summary")
    print(f"  Original: {total_origin}")
    print(f"  Removed:  {total_removed}")
    print(f"  Remaining:{total_origin - total_removed}")
    if args.dry_run:
        print(f"  [DRY-RUN] No files were deleted")
        print(f"  Run without --dry-run to apply")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
