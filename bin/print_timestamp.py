import sys
from datetime import datetime, timezone, timedelta

def convert_timestamp_to_jst(ms_timestamp):
    seconds = ms_timestamp / 1000.0
    utc_time = datetime.fromtimestamp(seconds, tz=timezone.utc)
    jst = utc_time.astimezone(timezone(timedelta(hours=9)))
    return jst.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' JST'

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_timestamp.py <UNIX milliseconds timestamp>")
        sys.exit(1)
    
    try:
        ms_timestamp = int(sys.argv[1])
        result = convert_timestamp_to_jst(ms_timestamp)
        print(result)
    except ValueError:
        print("Invalid input: please enter a numeric millisecond timestamp.")
        sys.exit(1)

if __name__ == "__main__":
    main()

