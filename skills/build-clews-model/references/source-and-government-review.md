# Source and government review

Create an exact, decision-oriented source register. The purpose is to let
country experts accept a source or propose a better national dataset. Do not
require redistribution of raw datasets or byte-for-byte comparison unless a
separate reproducibility or licensing requirement calls for it.

## Required source fields

Use one row per externally sourced variable or coherent product slice:

| Field | Required content |
|---|---|
| `source_id` | Stable local identifier |
| Provider | Institution responsible for the product |
| Product | Exact dataset or product name |
| Edition | Release, version, or publication date |
| Reference | Year, climatology, horizon, or scenario |
| Variable | Exact variable or element used |
| Unit | Source unit before conversion |
| Geography | Coverage and spatial resolution |
| Model use | Parameter, set, or structural choice affected |
| Selection | Filters, ranks, scenarios, or categories selected |
| Transformation | Aggregation, interpolation, conversion, or normalization |
| Quality | Official, estimated, imputed, modelled, or unknown |
| Proxy | Original item and substitute layer, when applicable |
| URL | Official landing page or catalogue entry |
| License | Reuse conditions or source license |
| National alternative | Candidate country-owned replacement |
| Review owner | Agency or technical office able to assess it |

Record enough metadata to distinguish, for example, a historical low-input
GAEZ layer from a future high-input climate layer. Do not write only `GAEZ`,
`FAOSTAT`, or `population data`.

## Crop source and proxy register

For each selected crop item, record:

- exact source item and code;
- harvested-area rank, value, unit, year, and quality flag;
- production value, unit, year, and quality flag when used as demand;
- explicit output or aggregate membership;
- exact GAEZ code and layer;
- irrigation/rain-fed and high/low-input combinations;
- climate model, pathway, and period;
- available-water-capacity assumption;
- proxy rationale and expected yield/water/climate differences.

Use exact item equality for joins. Reject substring matching, duplicate proxy
rasters, a crop appearing in both explicit and aggregate groups, and a proxy
code counted more than once.

## Government-review table

Add a concise table to `DATA_SOURCE_REGISTER.md`:

| Decision | Current source/assumption | Why it matters | Suggested reviewer | Better national data? | Status |
|---|---|---|---|---|---|

At minimum cover:

- administrative boundaries and model domain;
- seasons and time zone;
- crop selection, production anchors, and quality flags;
- crop proxies and aggregate crops;
- land cover;
- crop suitability and potential yield;
- precipitation and evapotranspiration;
- irrigation requirements and groundwater/surface-water availability;
- population or other demand-growth series;
- energy resource and technology applicability inputs.

The review table is not calibration. It identifies potential future source
substitutions without applying them during the raw build.

## Artifact

Create `DATA_SOURCE_REGISTER.md` from the template in
`references/handoff-templates.md`. Keep source choices synchronized with
`MODEL_CARD.md`, the country configuration, and generated parameters.
