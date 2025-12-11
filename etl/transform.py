# etl/extract.py
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    parser.add_argument("--full-reload", required=True)
    parser.add_argument("--run-date", required=True)
    parser.add_argument("--src-dsn", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print("In Transform Step")

    # Connect to source DB using args.src_dsn
    # Extract data based on env, full-reload, run-date
    # Write raw files to args.output_dir

if __name__ == "__main__":
    main()
