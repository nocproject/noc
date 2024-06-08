# Loading GIS data

It's `etl` process now, so you should create `Remote System` and use commands `noc etl extract <Name Remote System>`, `noc etl load <Name Remote System>`.
Aims of loading GIS data are the pulling into Division, Street, Building and Address models.
Sources of extractions are `FIAS` data and `OKTMO` data.

### Environment of Remote System:

- `CACHE_PATH` (dir for getting archive and csv files and extracting dbf files)
- `OKTMO_URL` (url for getting OKTMO archive file)
- `OKTMO_REGION` (region [code](oktmo-region-codes.md) of OKTMO data)
- `FIAS_URL` (url for getting FIAS archive file)
- `FIAS_REGION` (region [code](fias-region-codes.md) of FIAS data)

### Handler of Remote System:

- noc.core.etl.extractor.fias.FiasRemoteSystem

### Checkboxes Extractors/Loaders of Remote System:
(you should turn them on)

- Address
- Administrative-Territorial Division
- Building
- Street

## Example:

- `Name of Remote System`: `FIAS`
- `Handler`: `noc.core.etl.extractor.fias.FiasRemoteSystem`
- `Extractors/Loaders`: `Address`, `Administrative-Territorial Division`, `Building`, `Street`
- `CACHE_PATH`: `local/cache/fias`
- `OKTMO_URL`: `https://rosstat.gov.ru/opendata/7708234640-oktmo/data-20210401-structure-20150128.csv`
- `OKTMO_REGION`: `04`
- `FIAS_URL`: `https://fias-file.nalog.ru/downloads/2021.04.27/fias_dbf.zip`
- `FIAS_REGION`: `24`

![fias](fias-remote-system-scr.png)

#### Command of extracting:

```angular2html
./noc etl extract FIAS
```

#### Command of loading:

```angular2html
./noc etl load FIAS
```
