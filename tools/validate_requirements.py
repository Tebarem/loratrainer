import os
import sys
import shutil
import argparse
from setup_windows import install
from library.custom_logging import setup_logging

# Set up logging
log = setup_logging()


def check_torch():
    # Check for nVidia toolkit or AMD toolkit
    if shutil.which('nvidia-smi') is not None or os.path.exists(
        os.path.join(
            os.environ.get('SystemRoot') or r'C:\Windows',
            'System32',
            'nvidia-smi.exe',
        )
    ):
        log.info('nVidia toolkit detected')
    elif shutil.which('rocminfo') is not None or os.path.exists(
        '/opt/rocm/bin/rocminfo'
    ):
        log.info('AMD toolkit detected')
    else:
        log.info('Using CPU-only Torch')

    try:
        import torch

        log.info(f'Torch {torch.__version__}')

        # Check if CUDA is available
        if not torch.cuda.is_available():
            log.warning('Torch reports CUDA not available')
        else:
            if torch.version.cuda:
                # Log nVidia CUDA and cuDNN versions
                log.info(
                    f'Torch backend: nVidia CUDA {torch.version.cuda} cuDNN {torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else "N/A"}'
                )
            elif torch.version.hip:
                # Log AMD ROCm HIP version
                log.info(f'Torch backend: AMD ROCm HIP {torch.version.hip}')
            else:
                log.warning('Unknown Torch backend')

            # Log information about detected GPUs
            for device in [
                torch.cuda.device(i) for i in range(torch.cuda.device_count())
            ]:
                log.info(
                    f'Torch detected GPU: {torch.cuda.get_device_name(device)} VRAM {round(torch.cuda.get_device_properties(device).total_memory / 1024 / 1024)} Arch {torch.cuda.get_device_capability(device)} Cores {torch.cuda.get_device_properties(device).multi_processor_count}'
                )
                return int(torch.__version__[0])
    except Exception as e:
        log.error(f'Could not load torch: {e}')
        sys.exit(1)


def install_requirements(requirements_file):
    log.info('Verifying requirements')
    with open(requirements_file, 'r', encoding='utf8') as f:
        # Read lines from the requirements file, strip whitespace, and filter out empty lines, comments, and lines starting with '.'
        lines = [
            line.strip()
            for line in f.readlines()
            if line.strip() != ''
            and not line.startswith('#')
            and line is not None
            and not line.startswith('.')
        ]

        # Iterate over each line and install the requirements
        for line in lines:
            install(line)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Validate that requirements are satisfied.'
    )
    parser.add_argument(
        '-r',
        '--requirements',
        type=str,
        help='Path to the requirements file.',
    )
    parser.add_argument('--debug', action='store_true', help='Debug on')
    args = parser.parse_args()

    # Check Torch
    if check_torch() == 1:
        install_requirements('requirements_windows_torch1.txt')
    else:
        install_requirements('requirements_windows_torch2.txt')


if __name__ == '__main__':
    main()
