from glob import glob
from os.path import join
from tempfile import mkstemp
from PIL import Image, ImageOps, ImageChops, ImageFilter

THRESHOLD = 26


def threshold(img, t=127, invert=False):
    """
    Your standard threshold function.
    """
    def clamp (p):
        return 0 if p<t else 255

    def invert_clamp (p):
        return 0 if p>=t else 255

    gray = img.convert("L")
    clamp_func = clamp if not invert else invert_clamp
    return gray.point(clamp_func, 'L')


if __name__ == "__main__":
    # Load up images.
    search_dir = "photo"
    scan_path = glob(join(search_dir, "scan.*???"))[0]
    bg_path = glob(join(search_dir, "bg.*???"))[0]
    scan, bg = map(Image.open, [scan_path, bg_path])

    # Create difference map
    diff = ImageChops.difference(bg, scan)
    diff.save("just_diff.png")

    # Create noisey image mask
    clamped = threshold(diff, THRESHOLD)
    
    # Blur and then clamp to eliminate noise
    smudge = clamped.filter(ImageFilter.GaussianBlur(5))
    smudge_mask = threshold(smudge, invert=True)

    # Use smudge mask to remove most noise but leave original clamp.
    result = clamped.convert("RGB")
    result.paste((0,0,0), None, mask=smudge_mask)
    result.save("mask.png")
