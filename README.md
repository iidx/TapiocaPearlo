# TapiocaPearlo
Forensic Tool for discovering IoT environment.



## Usage

### Dependencies

* Docker

  ```bash
  curl -fsSL https://get.docker.com/ | sudo sh
  sudo usermod -aG docker $USER
  ```

* docker-compose

  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  sudo sysctl -w vm.max_map_count=262144
  ```

  You have to set vm.map_map_count as [262144] because the minimum requires for executing elasticsearch is over [262144] counts. 



### Run Tapioca docker service

You have to run docker services for configuring Tapioca

* Start

  ```bash
  docker-compose up -d --build
  ```

  Remove the `--build` option when you're already executed the service before.

* Access

  `tapioca_terminal` is a virtually isolated container for running tools efficiently.

  Because the container is completely isolated, you must move all the evidence into `tools` directory.

  ```bash
  docker exec -it tapioca_terminal /bin/bash
  ```


* Terminate

  If you don't want to use `TapiocaPearlo` anymore, execute the command for clean-up all services.

  ```bash
  docker-compose down
  ```



### Tools

All of TapiocaPearlo tools are located at `tools`.



#### Wink Activity Parser

```bash
python wink_activity_parser.py -d <WINK_DATABASE_FILE_PATH>
```



#### Nest Video Recovery Tool

```bash
python nest_video_recovery.py -d <NEST_DATABASE_FILE_PATH> -o <VIDEO_FILE_OUTPUT_DIRECTORY> -m <MERGE_VIDEO_CLIP> -f <EXTRACT_FRAME_BY_PNG> -a <UPLOAD_TO_ELASTICSEARCH>
```



#### iSmartAlarm Dairy Parser

```bash
python ismartalarm_dairy_parser.py -d <ISMARTALARM_DATABASE_FILE_PATH>
```



#### iSmartAlarm Server Stream Parser

```bash
python server_stream_parser.py -s <ISMARTALARM_SERVER_STREAM_FILE_PATH>
```


#### Amazon Alexa CIFT Tool Parser

```bash
python alexa_cift_parser.py -d <CIFT_DATABASE_FILE_PATH> -t <TIMEZONE>
```
