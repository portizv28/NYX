"""Ejecutar manualmente: .venv\\Scripts\\python scripts\\voice_calibrate.py"""

from voice.calibration import calibrate_noise


if __name__ == "__main__":
    result = calibrate_noise()
    print(f"RMS medio: {result.rms_average:.5f}")
    print(f"RMS pico: {result.rms_peak:.5f}")
    print(f"Umbral STT recomendado: {result.recommended_threshold:.5f}")
