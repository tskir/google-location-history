# google-location-history

## Install
```bash
sudo apt update
sudo apt -y install python3-mpltoolkits.basemap
sudo python3 -m pip install --upgrade -r requirements.txt
```

## Download Google location history data

## Run
```bash
python3 location.py \
  --location-history-json 'Location History.json' \
  --output-png 'location.png'
```