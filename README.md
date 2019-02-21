# TapiocaPearlo
Forensic Tool for discovering IoT environment.

## Developer
* Gyuho Lee ([@extr](https://github.com/iidx))
* Namjun Kim ([@bunseokbot](https://github.com/bunseokbot))


## Usage

### Wink Activity Parser
```
python wink_activity_parser.py -d <WINK_DATABASE_FILE_PATH>
```

### Nest Video Recovery Tool
```
python nest_video_recovery.py -d <NEST_DATABASE_FILE_PATH> -o <VIDEO_FILE_OUTPUT_DIRECTORY> -m <MERGE_VIDEO_CLIP> -a <UPLOAD_TO_ELASTICSEARCH>
```

### iSmartAlarm Dairy Parser
```
python ismartalarm_dairy_parser.py -d <ISMARTALARM_DATABASE_FILE_PATH>
```

### Amazon Alexa CIFT Tool Parser
```
python alexa_cift_parser.py -d <CIFT_DATABASE_FILE_PATH> -t <TIMEZONE>
```
