# Innovationsintensität und Firmenperformance europäischer KMU
### ExInt II | WU Vienna | SS 2026 | Anna Kramer

## Research Question
Wie beeinflusst R&D Intensität die Firmenperformance bei europäischen KMU,
und moderiert Firmengröße diesen Zusammenhang?

## Hypotheses
- **H1:** Höhere R&D Intensität führt zu besserer Firmenperformance
  bei europäischen KMU.
- **H2:** Firmengröße moderiert den Zusammenhang zwischen R&D
  Intensität und Performance positiv.

## Theoretical Foundation
**Absorptive Capacity (Cohen & Levinthal, 1990):**
Firmen mit höherer R&D Intensität entwickeln eine stärkere Fähigkeit externes
Wissen aufzunehmen und in Performance umzuwandeln.

**Resource-Based View (Barney, 1991):**
R&D Investitionen schaffen einzigartige, schwer imitierbare Ressourcen die
zu nachhaltigem Wettbewerbsvorteil führen.

## Variables

### Dependent Variable (Y)
| Construct | Data Item(s) | Formula |
|-----------|-------------|---------|
| RoA | nicon, at | nicon / at |
| EBITDA | ebitda | direct field |
| Sales Growth | sale | (sale_t - sale_t-1) / sale_t-1 |

### Independent Variable (X)
| Construct | Data Item(s) | Formula |
|-----------|-------------|---------|
| R&D Intensity | xrd, at | xrd / at |
| Capital Expenditure | capx, at | capx / at |

### Controls
| Construct | Data Item(s) | Formula |
|-----------|-------------|---------|
| Firm Size | at | log(at) |
| Leverage | dltt, dlc, seq | (dltt+dlc) / seq |
| Employees | emp | direct field |
| Cash Holdings | che, at | che / at |
| Tangibility | ppent, at | ppent / at |
| Total Assets | at | direct field |
| Total Liabilities | lt | direct field |
| Revenue | sale | direct field |
| Operating Income | oiadp | direct field |
| Depreciation | dp | direct field |
| Interest Expense | xint | direct field |
| Cash Flow Operations | oancf | direct field |
| Long-term Debt | dltt | direct field |
| Short-term Debt | dlc | direct field |
| Stockholders Equity | seq | direct field |
| Retained Earnings | re | direct field |
| Inventory | invt | direct field |
| Accounts Receivable | rect | direct field |
| Accounts Payable | ap | direct field |
| Current Assets | act | direct field |
| Current Liabilities | lct | direct field |
| Pretax Income | pi | direct field |
| Income Taxes | txt | direct field |
| SGA Expense | xsga | direct field |
| Cost of Goods Sold | cogs | direct field |
| Staff Expense | xlr | direct field |
| Intangible Assets | intan | direct field |
| Goodwill | gdwl | direct field |
| Working Capital | wcap | direct field |
| Gross Profit | revt, cogs | revt - cogs |
| Net Income | nicon | direct field |

## Data
- Source: WRDS / Compustat Global (g_funda)
- Sample: Europäische KMU gemäß EU-Definition (≤250 Mitarbeiter,
  Jahresumsatz ≤50 Mio. EUR oder Bilanzsumme ≤43 Mio. EUR),
  EUR-Währung, 2015-2024

## How to Reproduce
git clone https://github.com/kramerannaa/kmu-rd-performance
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
task all

## Data Provenance
| Item | Detail |
|------|--------|
| Source | WRDS / Compustat Global |
| Table | comp_global_daily.g_funda |
| Downloaded | 2026-05-28 |
| License | WRDS subscriber agreement |
| Fiscal years | 2015-2024 |
| Raw rows | 338,462 |
| Clean rows | 26,090 |
