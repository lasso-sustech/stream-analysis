# A Tool for Simple Stream Analysis

### How to user
1. touch `.traces` file, and put one line of the location to the traces root folder, e.g.,
    ```
    ./traces
    ```

2. touch `config.json` file and define the following sections to apply the analysis:
    ```json
    {
        "lap2tv.pcapng": {
            "filter": "<wireshark display filter>",
            "limit": "<(unit: ms) threshold for packet chop>",

            "interval_cutoff": "<(unit: s) the interval beyond the cutoff will not display>",

            "interval_percent": "<the majority for interval analysis>",
            "length_percent": "<the majority percent for length analysis>"
        }
    ```

3. run `python3 analyze.py` for analysis.
