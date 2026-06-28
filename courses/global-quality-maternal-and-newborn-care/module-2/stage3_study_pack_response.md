
<h2 class="sr-only">MNCH global quality maternal and newborn care — interactive study pack covering 9 core concepts, 5 clinical vignettes, evidence tables, checklists, and 20 active recall questions.</h2>
<style>
*{box-sizing:border-box;margin:0;padding:0}
.sp-root{font-family:var(--font-sans);color:var(--text-primary);padding:1rem 0 3rem}
.sp-header{margin-bottom:1.5rem}
.sp-meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.sp-chip{font-size:12px;padding:3px 10px;border-radius:20px;border:0.5px solid var(--border);color:var(--text-secondary);background:var(--surface-1)}
.sp-tabs{display:flex;gap:4px;border-bottom:0.5px solid var(--border);margin-bottom:1.5rem;overflow-x:auto}
.sp-tab{font-size:13px;padding:8px 14px;border:none;background:none;cursor:pointer;color:var(--text-secondary);border-bottom:2px solid transparent;white-space:nowrap;transition:color .15s}
.sp-tab.active{color:var(--text-accent);border-bottom-color:var(--border-accent);font-weight:500}
.sp-tab:hover:not(.active){color:var(--text-primary)}
.card{background:var(--surface-1);border:0.5px solid var(--border);border-radius:12px;margin-bottom:10px;overflow:hidden}
.card-hdr{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;cursor:pointer;gap:12px}
.card-hdr:hover{background:var(--surface-0)}
.card-title{font-size:14px;font-weight:500;flex:1}
.card-body{padding:0 16px 16px;border-top:0.5px solid var(--border)}
.evbadge{font-size:11px;padding:2px 8px;border-radius:20px;white-space:nowrap;font-weight:500}
.ev-H{background:var(--bg-success);color:var(--text-success)}
.ev-M{background:var(--bg-warning);color:var(--text-warning)}
.ev-D{background:var(--bg-danger);color:var(--text-danger)}
.ev-A{background:var(--bg-accent);color:var(--text-accent)}
.ev-bar{height:3px;border-radius:2px;margin-top:0;margin-bottom:12px}
.ev-bar-H{background:var(--border-success);width:100%}
.ev-bar-M{background:var(--border-warning);width:67%}
.ev-bar-L{background:var(--border-danger);width:33%}
.section-label{font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);margin:14px 0 6px}
.kp-list{list-style:none}
.kp-list li{font-size:13px;color:var(--text-secondary);padding:4px 0 4px 16px;position:relative;line-height:1.5;border-bottom:0.5px solid var(--border)}
.kp-list li:last-child{border-bottom:none}
.kp-list li::before{content:"›";position:absolute;left:0;color:var(--text-muted)}
.kp-list li.warn{color:var(--text-danger)}
.kp-list li.warn::before{content:"⚠";font-style:normal}
.stat-row{display:grid;grid-template-columns:1fr auto auto;gap:8px;align-items:center;font-size:12px;padding:5px 0;border-bottom:0.5px solid var(--border)}
.stat-row:last-child{border-bottom:none}
.stat-name{color:var(--text-secondary)}
.stat-val{font-family:var(--font-mono);font-size:11px;color:var(--text-accent);background:var(--bg-accent);padding:2px 6px;border-radius:4px;white-space:nowrap}
.stat-dir{font-size:12px;font-weight:500}
.dir-down{color:var(--text-success)}
.dir-up{color:var(--text-danger)}
.dir-flat{color:var(--text-muted)}
.src-row{font-size:11px;color:var(--text-muted);margin-top:10px;font-style:italic}
.vig-q{font-size:13px;background:var(--bg-accent);border:0.5px solid var(--border-accent);border-radius:8px;padding:10px 12px;margin:10px 0;color:var(--text-primary)}
.vig-disc-item{font-size:13px;color:var(--text-secondary);padding:5px 0 5px 14px;position:relative;border-bottom:0.5px solid var(--border);line-height:1.5}
.vig-disc-item::before{content:"→";position:absolute;left:0;color:var(--text-muted)}
.vig-disc-item:last-child{border-bottom:none}
.lesson-box{background:var(--bg-success);border:0.5px solid var(--border-success);border-radius:8px;padding:10px 12px;margin-top:10px;font-size:13px;color:var(--text-primary)}
.pitfall-box{background:var(--bg-danger);border:0.5px solid var(--border-danger);border-radius:8px;padding:10px 12px;margin-top:6px;font-size:13px;color:var(--text-primary)}
.quiz-card{background:var(--surface-1);border:0.5px solid var(--border);border-radius:12px;margin-bottom:8px;padding:14px 16px}
.quiz-num{font-size:11px;color:var(--text-muted);margin-bottom:6px}
.quiz-q{font-size:13px;font-weight:500;margin-bottom:10px;line-height:1.5}
.quiz-reveal-btn{font-size:12px;padding:5px 14px;border:0.5px solid var(--border-strong);border-radius:var(--radius);background:none;cursor:pointer;color:var(--text-secondary)}
.quiz-reveal-btn:hover{background:var(--surface-0)}
.quiz-ans{font-size:13px;color:var(--text-secondary);margin-top:10px;padding:10px 12px;background:var(--surface-0);border-radius:8px;line-height:1.6;border:0.5px solid var(--border)}
.cl-section{margin-bottom:16px}
.cl-section-hdr{font-size:13px;font-weight:500;padding:8px 12px;background:var(--bg-accent);border:0.5px solid var(--border-accent);border-radius:8px;margin-bottom:6px;color:var(--text-accent);cursor:pointer}
.cl-item{display:flex;align-items:flex-start;gap:8px;font-size:12px;color:var(--text-secondary);padding:5px 0;border-bottom:0.5px solid var(--border)}
.cl-item:last-child{border-bottom:none}
.cl-item label{cursor:pointer;line-height:1.5}
.ev-table{width:100%;border-collapse:collapse;font-size:12px}
.ev-table th{text-align:left;padding:6px 8px;font-weight:500;font-size:11px;color:var(--text-muted);border-bottom:0.5px solid var(--border-strong);text-transform:uppercase;letter-spacing:.05em}
.ev-table td{padding:7px 8px;border-bottom:0.5px solid var(--border);color:var(--text-secondary);vertical-align:top}
.ev-table tr:last-child td{border-bottom:none}
.ev-table tr:hover td{background:var(--surface-0)}
.tbl-outcome{color:var(--text-primary);font-weight:500}
.tbl-val{font-family:var(--font-mono);font-size:11px;color:var(--text-accent)}
.delay-block{border-left:3px solid var(--border-accent);padding-left:12px;margin-bottom:12px}
.delay-num{font-size:11px;font-weight:500;color:var(--text-accent);margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em}
.ci-tag{font-size:11px;color:var(--text-muted);font-family:var(--font-mono)}
.section-hdr{font-size:16px;font-weight:500;margin-bottom:4px}
.section-sub{font-size:13px;color:var(--text-secondary);margin-bottom:14px}
.chevron{transition:transform .2s;font-size:14px;color:var(--text-muted)}
.chevron.open{transform:rotate(180deg)}
.progress-bar-bg{height:3px;background:var(--border);border-radius:2px;margin-bottom:12px}
</style>

<div class="sp-root">
  <div class="sp-header">
    <div style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.08em;color:var(--text-accent);margin-bottom:6px">Global quality maternal and newborn care — stage 3 study pack</div>
    <div style="font-size:20px;font-weight:500">Midwifery, systems & mortality: clinical study pack</div>
    <div class="sp-meta">
      <span class="sp-chip"><i class="ti ti-files" aria-hidden="true"></i> 15 sources processed</span>
      <span class="sp-chip"><i class="ti ti-brain" aria-hidden="true"></i> 9 core concepts</span>
      <span class="sp-chip"><i class="ti ti-stethoscope" aria-hidden="true"></i> 5 vignettes</span>
      <span class="sp-chip"><i class="ti ti-list-check" aria-hidden="true"></i> 2 checklists</span>
      <span class="sp-chip"><i class="ti ti-refresh" aria-hidden="true"></i> 20 active recall questions</span>
    </div>
  </div>

  <div class="sp-tabs" id="tabs"></div>
  <div id="tab-content"></div>
</div>

<script>
const TABS=[{id:"concepts",label:"Core concepts"},{id:"vignettes",label:"Clinical vignettes"},{id:"evidence",label:"Evidence tables"},{id:"checklists",label:"Checklists"},{id:"quiz",label:"Active recall"}];

const concepts=[
{id:1,title:"Models of maternity care: the spectrum",evidence:"Moderate",sources:"S1 (Raipuria 2018) · S2 (Attanasio 2017) · S14 (Vedam 2018)",summary:"Maternity care exists on a spectrum from fully midwife-led continuity models to exclusively physician-led care, with significant variation in philosophy, intervention rates, and outcomes.",keyPoints:["Midwifery philosophy: pregnancy and childbirth as normal physiological events for most women — 'high-touch/low-intervention'","US anomaly: 90% of births physician-attended vs 50–75% midwife-attended in comparable OECD nations","Three structural models: (1) midwife-led continuity — same midwife/team from booking through postpartum; (2) obstetrician-led; (3) shared/team care","Continuity of carer = independent predictor of satisfaction and known midwife at birth","US MISS scores range 17–61/100: no US state achieves even two-thirds of conditions for full integration"],clinical:["Care model selection measurably influences intervention rates even after adjusting for individual clinical risk","Hospital-level midwifery percentage affects institutional procedure rates — cultural and structural effect","Regulatory frameworks (scope of practice, prescribing authority, governance) are the primary levers for change"],stats:[]},
{id:2,title:"Cochrane evidence: midwife-led continuity of care",evidence:"High",sources:"S4 (Sandall 2016 Cochrane Review)",summary:"The highest-quality synthesis (Cochrane 2016) demonstrates that midwife-led continuity models confer significant benefits across multiple maternal and neonatal outcomes. No adverse effects identified.",keyPoints:["15 RCTs, 17,674 women — largest synthesis of comparative maternity care evidence","All trials in high-income settings only (Australia, Canada, Ireland, UK) — direct LMIC applicability requires caution","No adverse effects for mothers or infants; economic analyses trend toward cost-saving","Higher maternal satisfaction in most included studies (narratively synthesized — not meta-analysed)","None of 15 trials evaluated out-of-hospital births; all involved qualified midwives in hospital or community-linked settings","Labor is ~0.50 hours longer under midwife-led care — important for patient counseling and resource planning"],clinical:["Evidence is robust enough to support policy expansion of midwife-led models for low-risk and mixed-risk populations","Cost-savings driven by reduced staff costs and fewer interventions — compelling health system argument","C-section rate is NOT significantly reduced — a common misconception; instrumental birth and preterm birth ARE reduced"],stats:[{o:"Regional analgesia",v:"RR 0.85",ci:"0.78–0.92",d:"↓"},{o:"Instrumental vaginal birth",v:"RR 0.90",ci:"0.83–0.97",d:"↓"},{o:"Preterm birth (<37 wks)",v:"RR 0.76",ci:"0.64–0.91",d:"↓"},{o:"Fetal loss + neonatal death",v:"RR 0.84",ci:"0.71–0.99",d:"↓"},{o:"Spontaneous vaginal birth",v:"RR 1.05",ci:"1.03–1.07",d:"↑"},{o:"Caesarean section",v:"RR 0.92",ci:"0.84–1.00",d:"~ (no sig. diff.)"},{o:"Postpartum haemorrhage",v:"No sig. difference",ci:"—",d:"~"},{o:"NICU admission",v:"No sig. difference",ci:"—",d:"~"}]},
{id:3,title:"Midwifery in hospital settings: individual-level comparative data",evidence:"High",sources:"S2 (Attanasio 2017) · S3 (Souter 2019) · S13 (McRae 2018)",summary:"Multiple cohort studies directly compare outcomes for low-risk women managed by midwives vs obstetricians within hospital settings, consistently showing reduced interventions — with one critical exception.",keyPoints:["Souter 2019: 23,100 births across 11 hospitals, 2014–2018 — largest US hospital-based comparative study","Midwifery care associated with lower rates of: induction, AROM, epidurals, oxytocin, episiotomies, operative vaginal births, and C-sections","WARN: Shoulder dystocia significantly INCREASED in multiparous patients under midwifery care (aRR 1.42, CI 1.04–1.92) — must be counseled for","Attanasio 2017: hospital-level effect — more midwife-attended births at an institution lowers procedure rates for ALL patients at that hospital","McRae 2018: 57,872 low-SES women in Canada — midwifery reduced SGA, PTB, and LBW vs both GP and OB care"],clinical:["Counsel multiparous patients choosing midwife-led care specifically about shoulder dystocia risk and emergency protocols","Hospital administrators: increasing midwifery presence benefits institutional procedure rates through culture change","Equity impact: midwifery confers strongest benefit in low-socioeconomic populations — powerful policy argument"],stats:[{o:"C-section, nulliparous",v:"aRR 0.68",ci:"0.57–0.82",d:"↓ ~30%"},{o:"C-section, multiparous",v:"aRR 0.57",ci:"0.36–0.89",d:"↓ ~40%"},{o:"Operative vaginal, nulliparous",v:"aRR 0.73",ci:"0.57–0.93",d:"↓"},{o:"Operative vaginal, multiparous",v:"aRR 0.30",ci:"0.14–0.63",d:"↓"},{o:"⚠ Shoulder dystocia, multiparous",v:"aRR 1.42",ci:"1.04–1.92",d:"↑ RISK"},{o:"C-section (hospital-level, 15–40% midwife)",v:"aOR 0.70",ci:"0.59–0.82",d:"↓"},{o:"Episiotomy (hospital-level, >40% midwife)",v:"aOR 0.41",ci:"0.23–0.74",d:"↓"},{o:"SGA vs OB (low-SES population)",v:"aOR 0.59",ci:"0.50–0.69",d:"↓"},{o:"PTB vs OB (low-SES population)",v:"aOR 0.53",ci:"0.45–0.62",d:"↓"},{o:"LBW vs OB (low-SES population)",v:"aOR 0.43",ci:"—",d:"↓"}]},
{id:4,title:"The three delays model: framework for maternal mortality analysis",evidence:"High",sources:"S10 (Prevention of Maternal Mortality Program) · S6 (Van Lerberghe 2014)",summary:"The Three Delays Model explains maternal deaths through three sequential failure points in the obstetric emergency pathway, each requiring distinct system interventions.",keyPoints:["Delay 1 — decision to seek care: modified by perceived severity, gender dynamics, socioeconomic status, cultural factors, and cost","Delay 2 — travel to facility: distance, transport availability, road quality, cost of transport","Delay 3 — care at facility: staff shortages, drug/supply shortages, administrative delays, clinical mismanagement","KEY: Arriving at a facility ≠ receiving adequate care — facility-level failures are 'documentable contributors to maternal deaths'","Patient preference: evidence suggests women often prioritize care quality over financial cost when decisions are possible"],clinical:["Expanding facility number (BEmONC/CEmONC) addresses Delay 2 but does NOT address Delay 3 without quality investment","Community mobilization, transport schemes, and birth waiting homes target Delay 1 and Delay 2","Death audits and near-miss reviews are the evidence-based mechanism for identifying and addressing Delay 3 failures","Referral systems are a critical Delay 2/3 bridge — weak referral pathways are as lethal as distance"],stats:[]},
{id:5,title:"Global maternal mortality burden: epidemiology and measurement",evidence:"High",sources:"S5 (Shaw 2016) · S11 (CDC PMSS) · S12 (GBD 2015)",summary:"Global maternal mortality declined substantially between 1990 and 2015, but progress was uneven, hemorrhage remains the dominant preventable cause in low-resource settings, and measurement systems remain weak.",keyPoints:["GBD 2015: maternal mortality declined globally 1990–2015, but progress was uneven across regions and development levels","Burden concentrated in low-SDI settings — reinforcing the equity dimension of maternal mortality","Hemorrhage: dominant cause of maternal death in low-resource settings; higher-SDI settings show more indirect maternal causes","Substandard care: almost half of maternal deaths in France, Netherlands, and UK are associated with substandard care","PMSS definition: pregnancy-related death = death during pregnancy OR within ONE YEAR after end of pregnancy from cause related to or aggravated by pregnancy","Surveillance gap: UK vital registration captured only 53% of maternal deaths in one enquiry; Canada's system identified only 41% (1997–2000)"],clinical:["Hemorrhage prevention and management (AMTSL, tranexamic acid, blood product access) = highest-yield intervention in low-resource settings","Surveillance systems must use the 1-year postpartum window (PMSS standard) to avoid undercounting indirect and late maternal deaths","HIC maternal deaths are not a 'solved problem' — substandard care is a major driver even in wealthy health systems"],stats:[]},
{id:6,title:"Health systems strengthening in LMICs: the Cambodia pathway",evidence:"High",sources:"S6 (Van Lerberghe 2014) · S7 (WHO/Cambodia 2015) · S8 (MoH Cambodia 2014)",summary:"Cambodia achieved dramatic reductions in maternal and child mortality through a sequential, pragmatic approach to health system strengthening, providing a replicable model with important lessons about quality gaps.",keyPoints:["The four-step virtuous cycle (Van Lerberghe): facility expansion → workforce scale-up → financial barrier removal → (delayed) quality improvement","Government Midwifery Incentive Scheme (GMIS): USD $15/live birth at health centres, $10 at hospitals — dramatically increased institutional delivery after 2007 rollout","Health Equity Funds (HEFs) + vouchers: demand-side financing that removed financial barriers for poorest populations","Newborn mortality: the persistent gap — 50% of all under-5 deaths by 2010, mostly in first 24 hours — immediate newborn care quality remains inadequate","Exclusive breastfeeding: 11% → 74% (2000–2010) through mass media campaigns and health system support","The four-step cycle was SEQUENTIAL — quality was last and remains the most neglected element globally"],clinical:["Supply-side incentives (GMIS) pull women into facilities but do not automatically improve quality of care received","Demand-side financing (HEFs, vouchers) is essential for equity — coverage without access for the poorest is meaningless","Newborn mortality requires specific investment in intrapartum care quality — facility count expansion is necessary but insufficient"],stats:[{o:"MMR (national data)",v:"432 → 206",ci:"/100,000 LB",d:"↓ 52% (2000–2010)"},{o:"MMR (inter-agency estimate)",v:"1,200 → 170",ci:"/100,000 LB",d:"↓ 86% (1990–2013)"},{o:"Skilled birth attendance",v:"32% → 84%",ci:"2000–2013",d:"↑"},{o:"Facility delivery rate",v:"10% → 80%",ci:"2000–2013",d:"↑"},{o:"ANC 4+ visits",v:"9% → 59%",ci:"2000–2010",d:"↑"},{o:"BEmONC facilities",v:"25 → 96",ci:"2009–2013",d:"↑"},{o:"CEmONC facilities",v:"19 → 36",ci:"2009–2013",d:"↑"},{o:"Exclusive breastfeeding",v:"11% → 74%",ci:"2000–2010",d:"↑"}]},
{id:7,title:"'Too much, too soon' vs 'too little, too late': the global paradox",evidence:"Moderate",sources:"S5 (Shaw 2016) · S6 (Van Lerberghe 2014) · S15 (Renfrew 2019)",summary:"Global maternal health is characterized by a paradox: low-resource settings suffer from insufficient access to essential care, while high-resource settings increasingly over-medicalize low-risk births — sometimes simultaneously within the same system.",keyPoints:["'Too little, too late' (TLTL): inadequate access, facility shortage, financial barriers, workforce gaps — primary challenge in LMICs","'Too much, too soon' (TMTS): over-medicalization of normal birth — unnecessary C-sections, inductions, episiotomies — primary challenge in HICs and emerging economies","The paradox can coexist within one country: wealthy women over-medicalized, poor women under-served","Drivers of TMTS in HICs: fear of litigation (US malpractice premiums correlate with higher C-section rates), epidemiological trends (↑obesity, ↑maternal age), hospital culture, physician economics","Not all intervention increases are inappropriate: rising maternal obesity (13% of Swedish mothers in 2014) and advanced maternal age genuinely increase obstetric complexity"],clinical:["Quality assessment must distinguish necessary vs unnecessary interventions — not all high C-section rates signal over-medicalization","Disparities within HICs: minority and migrant populations often experience TLTL within systems that over-treat majority populations","Midwifery integration addresses TMTS without creating TLTL — the evidence-based solution to both poles"],stats:[]},
{id:8,title:"Midwifery integration, equity, and outcomes: the MISS framework",evidence:"High",sources:"S13 (McRae 2018) · S14 (Vedam 2018)",summary:"The Midwifery Integration Scoring System (MISS) provides a validated, quantitative method for measuring how well midwives are integrated into health systems, with strong correlations between integration scores and maternal-newborn outcomes.",keyPoints:["MISS: 50 weighted indicators from 110 regulatory variables, validated by 92 state/national experts","Dimensions measured: scope of practice, provider autonomy, governance, prescriptive authority, interprofessional collaboration, birth setting access","Equity finding: states with lower MISS scores have higher proportions of Black births AND lower midwife density — compounding disadvantage","MISS + Black birth proportion together explained 50.1% of variance in US neonatal mortality rates","Community birth rates increased 72% across US states between 2004–2014; higher MISS → larger increases","WARN: MISS did NOT add significant explanatory power for C-section and LBW rates after controlling for race — race remains the dominant driver for those outcomes"],clinical:["Policy levers: scope-of-practice law, independent prescribing rights, birth setting access, CPM licensure, hospital privileges","Racial equity and midwifery integration are interlinked — midwifery expansion is simultaneously an equity and quality intervention","MISS framework could be adapted for other national health systems (including Kenya) to audit midwifery integration status"],stats:[{o:"MISS range (US states)",v:"17–61",ci:"out of 100",d:"No state achieves even ⅔"},{o:"Neonatal mortality variance: MISS + race",v:"50.1%",ci:"MISS alone: 11.6% additional",d:"p=0.002"},{o:"Community birth rate increase",v:"72% avg",ci:"2004–2014 across US",d:"↑"}]},
{id:9,title:"Barriers to global midwifery progress: why evidence isn't enough",evidence:"Moderate",sources:"S15 (Renfrew 2019)",summary:"Despite strong evidence, midwifery remains chronically under-invested globally. The root cause is intersecting gender, professional, and economic disempowerment of both midwives and the women they serve.",keyPoints:["Root cause: midwives and their patients are predominantly female — structural discrimination disadvantages both simultaneously","Specific barriers: inadequate remuneration, conflation of midwifery with nursing, workload overload, occupational violence, exclusion from senior leadership","Research gap: 100+ trials on community health workers in LMICs vs vastly less research on professional midwives — evidence base skewed toward task-shifting","Fragmented care: misunderstanding of midwifery scope creates handoff points → safety and quality gaps","Countries with long-established midwifery (Nordic countries) consistently show lowest maternal and newborn mortality","Sub-Saharan Africa (Ghana, Zambia, Somalia) and South Asia (Bangladesh, Nepal) making progress as of 2019"],clinical:["Health system reform for midwifery requires addressing gender equity as a structural precondition, not just a values statement","Professional regulation and independent prescribing are non-negotiable for full-scope practice","IPE + clear role delineation reduces intrapartum communication failures — a primary determinant of intrapartum neonatal death (Source 14)"],stats:[]}
];

const vignettes=[
{id:1,title:"Vignette 1: the care model decision",scenario:"A 26-year-old primigravida presents at 10 weeks gestation for antenatal booking. She is low-risk: no prior obstetric complications, no comorbidities, BMI 23, non-smoker. She asks: 'Should I see a midwife or a doctor for my care? What difference does it really make?'",question:"Based on the current evidence base, how would you counsel this patient about the clinical journey she might expect depending on her care model?",framework:"Apply: Cochrane 2016 (S4), Souter 2019 (S3), McRae 2018 (S13)",points:["Under midwife-led continuity care, she is significantly less likely to receive regional analgesia (epidural), undergo episiotomy or instrumental birth, or deliver preterm (Cochrane RR 0.76 for PTB).","She is significantly more likely to have a spontaneous vaginal birth (RR 1.05) and be attended at birth by someone she knows — strongly associated with satisfaction.","No significant difference in C-section rate between models (Cochrane RR 0.92, CI touches 1.0). Labor may be ~30 minutes longer under midwifery care.","No increased risk of postpartum hemorrhage, NICU admission, or other adverse outcomes under midwifery care.","She will NOT experience increased shoulder dystocia risk — that finding (Souter 2019, aRR 1.42) applies to multiparous patients only; this patient is nulliparous.","If she were low-SES, midwifery care would additionally reduce odds of SGA (aOR 0.59 vs OB) and preterm birth (aOR 0.53 vs OB) per McRae 2018."],lesson:"For low-risk primiparous women, midwife-led continuity care offers clear intervention-reduction benefits with no identified harm tradeoffs. All evidence is from HICs — counsel appropriately if context differs.",pitfall:"Do not cite the shoulder dystocia finding for this patient — it only applies to multiparous women."},
{id:2,title:"Vignette 2: the rural obstetric emergency",scenario:"A 32-year-old G3P2 develops sudden heavy vaginal bleeding at 36 weeks gestation. She is 48km from the nearest district hospital. The local health centre has one nurse-midwife, no blood products, and no emergency transport. Her husband is reluctant to take her due to cost fears.",question:"Apply the Three Delays Model to identify where this emergency is most vulnerable to fatal delay, and propose one specific intervention for each delay.",framework:"Apply: Three Delays Model (S10), Cambodia health systems evidence (S7, S8), Van Lerberghe LMIC pathway (S6)",points:["DELAY 1 (decision to seek care): husband's hesitation = gender dynamics + financial anxiety + prior bad experience with facilities. Intervention: community health worker networks, male partner antenatal engagement programs, pre-birth emergency planning, health equity fund insurance pre-enrollment.","DELAY 2 (reaching facility): 48km with no emergency transport = catastrophic for antepartum hemorrhage. Intervention: community transport schemes, maternity waiting homes near the district hospital, motorcycle ambulances, mobile-phone-based referral systems.","DELAY 3 (care at facility): no blood products + single midwife = inability to manage hemorrhage even if she arrives. Intervention: district blood bank supply chain, BEmONC skill-building for the nurse-midwife, telemedicine support protocol, clear referral pathway to CEmONC center.","This scenario illustrates the 'documentable contributors to maternal death' from Source 10: staff shortage + supply shortage + referral pathway failure compound across all three delays simultaneously.","Cambodia's GMIS addressed Delay 1 (financial barrier for delivery) and partly Delay 2 (incentivizing facility birth), but the persistent gap was Delay 3 — quality of care once in the facility."],lesson:"Each delay is independently lethal. Fixing one delay without addressing the others produces false security. Comprehensive systems, not just facility expansion, are required.",pitfall:"The Three Delays are not always sequential — in practice they overlap and compound simultaneously during an emergency."},
{id:3,title:"Vignette 3: the hospital administrator's C-section rate",scenario:"A hospital administrator in New York notices his facility's C-section rate is 38% among low-risk women. A neighboring hospital with similar patient demographics has a 23% rate. On investigation: the neighboring hospital has 32% midwife-attended births; his hospital has 7%. His obstetric department argues 'our patients are just sicker.'",question:"What does the evidence say about whether midwifery integration explains this difference, and what would a rigorous intervention program look like?",framework:"Apply: Attanasio 2017 (S2), Vedam MISS framework (S14), Shaw HIC drivers (S5)",points:["Attanasio 2017 is directly applicable: hospitals with 15–40% midwife-attended births have an aOR of 0.70 for C-section vs 0% midwife hospitals — the neighboring hospital's lower rate is consistent with this evidence.","The administrator's objection ('sicker patients') is testable: Attanasio studied low-risk patients specifically — the effect persists after risk adjustment.","However, correlation ≠ causation: the neighboring hospital's culture, patient mix, and physician attitudes may all contribute independently. MISS examines structural integration, not individual decisions.","Litigation climate is also relevant (Shaw 2016): fear of malpractice in high-premium states drives defensive C-section decisions — a systemic driver not visible in a simple hospital comparison.","An evidence-based intervention program: audit current midwife scope-of-practice regulations, establish collaborative care protocols, embed midwives in L&D, track monthly C-section rates by provider type, implement audit-and-feedback loops."],lesson:"Hospital-level midwifery culture appears to influence procedure rates across all patients at an institution, not just those directly under midwifery care. Systems change, not individual provider change, is the primary target.",pitfall:"Don't over-attribute C-section rate differences to midwifery presence alone — rule out patient risk mix, surgeon case volume, and hospital culture as confounders first."},
{id:4,title:"Vignette 4: the LMIC health minister's strategy",scenario:"A Health Minister reviews national data: MMR 480/100,000 LB, skilled birth attendance 28%, facility delivery rate 22%, BEmONC facilities covering 40% of districts. She has 5 years and a fixed budget. She asks her advisors to prioritize interventions.",question:"Based on the Cambodia evidence and the LMIC health systems literature, what is the most evidence-aligned sequence of priorities? What is the most commonly neglected element?",framework:"Apply: Van Lerberghe four-step cycle (S6), Cambodia case study (S7, S8), Three Delays Model (S10)",points:["Evidence-aligned sequence: FIRST — expand facility infrastructure (BEmONC/CEmONC to all districts) to address Delay 2 and give the workforce somewhere to deploy. A midwife without a facility to work in cannot reduce mortality.","SECOND — rapid midwifery workforce scale-up: consider Cambodia's 3-year direct entry model rather than a longer nursing+midwifery pathway to fast-track deployment. GMIS-equivalent incentive scheme to motivate rural posting.","THIRD — financial barrier removal: Health Equity Funds, free delivery policy, transport vouchers. Cambodia's GMIS created supply-side pull; HEFs created demand-side access — both are required for equity.","FOURTH (most neglected globally) — quality of care: maternal death audits, skilled immediate newborn care (ENBC, KMC), respectful care protocols, EmONC emergency drills. Cambodia's persistent gap: 50% of U5 deaths remained neonatal even after achieving 80% facility delivery.","The Minister must invest early in maternal death surveillance — measurement systems must precede the interventions they are designed to track."],lesson:"Facility delivery without quality care is a false win. The Cambodia lesson: high coverage + poor immediate newborn care = slow neonatal mortality decline. Quality must be built in parallel, not added as an afterthought.",pitfall:"Do not conflate 'facility delivery' with 'safe delivery' — they are not the same measure and reporting them interchangeably masks quality failures."},
{id:5,title:"Vignette 5: the maternal death audit finding",scenario:"A confidential maternal death review in a UK regional referral hospital finds that 9 of 17 maternal deaths over 3 years were associated with substandard care: postpartum haemorrhage (3 deaths, delayed recognition and transfusion), pre-eclampsia (3 deaths, delayed antihypertensive and MgSO4 initiation), indirect causes (3 deaths, late clinical escalation). The committee asks: is this typical, and what does the evidence say about prevention?",question:"Situate these findings in the global evidence base for HIC maternal mortality, and identify the evidence-based systemic interventions most likely to prevent recurrence.",framework:"Apply: Shaw HIC drivers (S5), CDC PMSS (S11), GBD 2015 (S12), Renfrew barriers (S15), Three Delays Delay 3",points:["This finding is consistent with international data: Shaw 2016 reports that almost half of maternal deaths in France, Netherlands, and UK involve substandard care. The audit's 53% rate is higher than average but not exceptional.","These deaths represent a failure of Delay 3 — care at the facility. The women arrived; they were not managed adequately. This is a quality failure, not an access failure.","Surveillance: PMSS-equivalent systems with medical epidemiologist review (including the 1-year postpartum window and indirect causes) are the evidence-based mechanism for identifying these patterns systematically — vital registration alone misses them.","Prevention evidence: midwife-physician team-based care with explicit escalation protocols reduces communication failure deaths (Source 14 — poor communication is a primary determinant of intrapartum death during critical obstetric events).","Standardized obstetric emergency simulation drills (ALSO, MOET) address clinical recognition speed and response time. IPE training specifically targets team communication failures — the mechanism behind the three indirect maternal deaths."],lesson:"HIC maternal mortality is substantially preventable. Substandard care at the facility level — Delay 3 — is the dominant modifiable driver in well-resourced settings. These are system failures, not clinical inevitabilities.",pitfall:"Do not assume HIC maternal death is random or unavoidable. Almost half are associated with documented substandard care — meaning they were preventable."}
];

const quizData=[
{q:"The Cochrane 2016 systematic review (Sandall) found that midwife-led continuity of care significantly reduced preterm birth. What was the relative risk, confidence interval, and how many studies contributed this finding?",a:"RR 0.76 (95% CI 0.64–0.91), based on 8 studies involving 13,238 participants. Sensitivity analysis restricted to low risk-of-bias trials showed an even larger effect: RR 0.64 (95% CI 0.51–0.81). All trials were conducted in high-income settings only."},
{q:"Name the three delays in the maternal mortality framework and give one system-level intervention for each.",a:"Delay 1 (decision to seek care): community health workers, male partner engagement programs, HEF pre-enrollment. Delay 2 (reaching facility): community transport schemes, maternity waiting homes, mobile referral systems. Delay 3 (receiving care at facility): maternal death audits, BEmONC drug supply chains, emergency obstetric drills, staffing protocols."},
{q:"What was Cambodia's maternal mortality ratio in 2000 and 2010 per national DHS data, and what four-step pathway drove this change?",a:"MMR declined from 432/100,000 LB in 2000 to 206/100,000 LB in 2010 (52% reduction). Four-step pathway: (1) expand facility infrastructure (BEmONC/CEmONC), (2) scale up midwifery workforce (3-year direct entry training), (3) remove financial barriers (GMIS, HEFs, vouchers), (4) quality improvement — delayed and still inadequate, the persistent gap."},
{q:"According to Souter 2019, what is the adjusted relative risk reduction in caesarean delivery for multiparous women under midwifery care — and what adverse outcome is INCREASED?",a:"C-section: aRR 0.57 (95% CI 0.36–0.89) ≈ 40% reduction vs obstetrician care. Adverse outcome INCREASED: shoulder dystocia in multiparous patients — aRR 1.42 (95% CI 1.04–1.92). This must be included in counseling for any multiparous woman choosing midwife-led care."},
{q:"How does PMSS define a 'pregnancy-related death,' and why is this definition clinically significant?",a:"PMSS defines pregnancy-related death as death during pregnancy OR within ONE YEAR after the end of pregnancy, from a cause related to or aggravated by pregnancy or its management. This is clinically significant because narrower definitions (e.g., within 42 days) miss late maternal deaths from indirect causes — cardiomyopathy, substance use disorders, suicide — which are increasingly major contributors in HICs."},
{q:"What was the adjusted odds ratio for episiotomy in hospitals with >40% midwife-attended births compared to hospitals with 0% midwife-attended births? (Attanasio 2017)",a:"aOR 0.41 (95% CI 0.23–0.74) — a 59% reduction in episiotomy odds. This is a hospital-level analysis; the effect reflects both direct midwifery practice and institutional culture change at higher midwifery proportions."},
{q:"What percentage of US births were attended by midwives in 2015, and how does this compare to other OECD high-income countries?",a:"~10% of US births attended by midwives (8.5% CNMs/CMs + 0.8% other midwives). 89.8% attended by physicians. Comparable OECD high-income countries: 50–75% of births midwife-attended."},
{q:"What are the MISS score ranges for the lowest and highest integrated US states, and what does the overall range imply?",a:"North Carolina: 17/100 (lowest); Washington State: 61/100 (highest). The range implies even the most integrated US state achieves less than two-thirds of conditions required for full midwifery integration — the entire country operates below optimal integration."},
{q:"In McRae 2018 (57,872 low-SES Canadian women), what were the adjusted odds ratios for preterm birth under midwifery care vs (a) GP care and (b) obstetrician care?",a:"PTB vs GP care: aOR 0.74 (95% CI 0.63–0.86). PTB vs OB care: aOR 0.53 (95% CI 0.45–0.62). Midwifery care showed the greatest PTB reduction vs obstetrician care — relevant given PTB is the leading cause of neonatal mortality globally."},
{q:"According to the Lancet 2016 analysis (Shaw), what proportion of maternal deaths in France, Netherlands, and UK are associated with substandard care?",a:"Almost half (~50%) of maternal deaths in these high-income countries are associated with substandard care, identified through confidential enquiries. This demonstrates HIC maternal mortality is substantially preventable — not random or inevitable."},
{q:"What was the GMIS payment structure in Cambodia, and what outcome was it associated with?",a:"GMIS paid USD $15 per live birth at health centres and $10 at referral hospitals, shared among facility staff, village health support groups, and village chiefs. The nationwide rollout in late 2007 was associated with a substantial rise in facility deliveries between 2006–2009."},
{q:"In Cochrane 2016, was there a significant difference in caesarean section rates between midwife-led continuity care and other models? What does the statistical result show?",a:"No statistically significant difference. RR 0.92 (95% CI 0.84–1.00). The confidence interval touches 1.00 — the result does not cross the threshold for statistical significance. Midwife-led continuity care does NOT significantly reduce caesarean rates. It reduces instrumental birth, episiotomy, analgesia, and preterm birth, but C-section rates are not significantly affected."},
{q:"What percentage of variance in US neonatal mortality rates did MISS scores and Non-Hispanic Black birth proportion together explain?",a:"50.1% of variance. Black birth proportion explained 38.5%; MISS scores explained an additional 11.6% (p=0.002) above and beyond race. MISS integration has an independent effect on neonatal mortality separate from the baseline racial disparity burden."},
{q:"What are three structural barriers to global midwifery progress identified by Renfrew 2019, and what root cause do they share?",a:"Any three of: inadequate remuneration; conflation with nursing; exclusion from senior leadership; workload overload; occupational violence; fragmented care; skewed research investment toward obstetric interventions. Root cause: intersectionality of gender inequality and professional disempowerment — midwives and the women they serve are both predominantly female and subject to the same structural discrimination."},
{q:"What was Cambodia's exclusive breastfeeding rate in infants under 6 months in 2000 vs 2010, and what intervention drove this change?",a:"Exclusive breastfeeding rose from 11% in 2000 to 74% in 2010. Key intervention: mass media campaign (TV spots, radio, soap operas) evaluated by the BBC World Service Trust in 2006, alongside health system training and NGO community education. Attribution to the campaign alone is not established — multiple concurrent interventions contributed."},
{q:"What was the key geographic limitation of the Cochrane 2016 systematic review of midwife-led continuity care?",a:"ALL 15 included trials were conducted in high-income settings (Australia, Canada, Ireland, and the UK). There were NO trials in resource-constrained countries. Direct applicability to settings like rural sub-Saharan Africa, South Asia, or other LMICs cannot be assumed without structural contextual adaptation. Additionally, no trial evaluated out-of-hospital births."},
{q:"According to Van Lerberghe 2014, what was the most consistently neglected element of the health systems strengthening pathway in high-maternal-mortality countries?",a:"Quality of care — specifically addressing over-medicalisation (unnecessary C-sections, routine augmentation, antibiotic overuse) and respectful, woman-centred care. Quality occurred LAST in the strengthening process and remains a significant blind spot globally. Systems focused on coverage (getting women to facilities) without commensurate investment in the quality of care received — evidenced by Cambodia's persistently slow neonatal mortality decline even after achieving 80% facility delivery."},
{q:"In the MISS study (Vedam 2018), what was the important null finding that should not be overlooked?",a:"MISS scores did NOT add significant explanatory power for caesarean section rates and low birth weight rates after controlling for race. The study's positive correlations with neonatal mortality, preterm birth, VBAC, and breastfeeding are strong — but MISS integration did not independently explain variance in C-section and LBW outcomes once race was accounted for. Race remains the dominant structural driver for those outcomes."},
{q:"Can 'too much, too soon' and 'too little, too late' coexist within a single country? Provide an example.",a:"Yes. TLTL (inadequate access, under-served populations) and TMTS (over-medicalization of normal birth) can coexist within one country. The US is a documented example: high overall C-section rates alongside elevated mortality among Black and Indigenous populations who face access barriers and receive inferior care quality. Shaw 2016 describes this as a compound injustice — minority and migrant populations often experience TLTL within systems that over-treat majority populations."},
{q:"What specific research gap does Renfrew 2019 identify regarding the evidence base for midwifery vs community health worker care in LMICs?",a:"Over 100 randomized controlled trials have been conducted on non-professional community health workers in LMICs, while professional midwives have been studied far less in those same settings. Research investment has been systematically skewed toward task-shifting to non-professional workers rather than building evidence for professional midwifery — contributing to policy decisions that undervalue midwifery training and deployment globally."}
];

const checklists=[
{id:0,title:"Three delays assessment checklist",subtitle:"Use for any maternal emergency or near-miss review to identify failure points",sections:[
{title:"Delay 1: decision to seek care",items:["Was the obstetric emergency recognized as serious by the woman or her household?","Were there gender-based barriers to decision-making (partner/family authority over woman's decisions)?","Were there financial fears about cost of care that delayed the decision?","Was there prior negative experience with health facilities that created hesitation?","Were cultural or traditional care-seeking behaviors a factor?","Was the woman's perceived severity of illness accurate?"]},
{title:"Delay 2: reaching the facility",items:["What was the distance (km) to the nearest BEmONC facility?","Was transport available? If not, what was the delay in obtaining it?","Were road conditions (seasonal flooding, road quality) a barrier?","Was the cost of transport prohibitive?","Was the woman transferred from a lower-level facility, and what was the referral delay?","Was there a functioning referral protocol and communication channel between facilities?"]},
{title:"Delay 3: care at the facility",items:["Was a qualified skilled birth attendant present on arrival?","Were essential emergency drugs available? (Oxytocin, MgSO4, antihypertensives, blood products)","Were essential equipment and supplies available? (IV access, suction, resuscitation equipment)","Was there administrative delay in registration, triage, or payment authorization?","Was clinical recognition of the emergency prompt and accurate?","Was interprofessional communication between midwife and physician team adequate?","Was a functional referral to higher-level care possible if required?","Was a maternal death review conducted and are findings being actioned?"]}
]},
{id:1,title:"Quality of maternity care assessment indicators",subtitle:"Based on global quality frameworks from the module sources",sections:[
{title:"Access and coverage indicators",items:["ANC 4+ visits rate (target: >80% of pregnant women nationally)","Skilled birth attendance rate (target: >90%)","Facility delivery rate — note: not equivalent to quality delivery; a proxy measure only","BEmONC facilities: at least 5 per 500,000 population","CEmONC facilities: at least 1 per 500,000 population","Geographic coverage: proportion of population within 2 hours of an EmONC facility"]},
{title:"Process and quality indicators",items:["Active management of third stage of labour (AMTSL) rate","Use of partograph in labor monitoring","Availability of 7 signal functions in BEmONC facilities","C-section rate within WHO target range (10–15% at population level)","Episiotomy rate (routine episiotomy should be 0%)","Exclusive breastfeeding rate at 6 months (target: ≥50%)","Maternal death-to-near-miss ratio — identifies audit system quality"]},
{title:"Outcome and equity indicators",items:["Maternal mortality ratio (per 100,000 live births) tracked annually","Stillbirth rate (per 1,000 total births)","Neonatal mortality rate (per 1,000 live births) — especially Day 1 deaths","Preterm birth rate","Maternal and neonatal mortality disaggregated by wealth quintile, geography, education level","Proportion of maternal deaths with substandard care identified at audit","Vacancy rate for midwifery posts in rural/remote facilities"]}
]}
];

let activeTab="concepts";
let openConcept=null;
let openVignette=null;
let revealed={};
let openClSection={0:{0:false,1:false,2:false},1:{0:false,1:false,2:false}};
let checks={};

function renderTabs(){
  const el=document.getElementById("tabs");
  el.innerHTML=TABS.map(t=>`<button class="sp-tab${t.id===activeTab?" active":""}" onclick="switchTab('${t.id}')">${t.label}</button>`).join("");
}

function switchTab(id){activeTab=id;openConcept=null;openVignette=null;renderTabs();renderContent();}

function dirClass(d){
  if(d.startsWith("↓"))return"dir-down";
  if(d.startsWith("↑"))return"dir-up";
  return"dir-flat";
}

function renderConcepts(){
  return`<div class="section-hdr">Core concepts</div>
<div class="section-sub">9 high-yield areas drawn from all 15 source cards. Select any concept to expand.</div>
${concepts.map((c,i)=>{
const open=openConcept===i;
const ev=c.evidence;
const evClass=ev==="High"?"ev-H":ev==="Moderate"?"ev-M":"ev-D";
const barClass=ev==="High"?"ev-bar-H":ev==="Moderate"?"ev-bar-M":"ev-bar-L";
return`<div class="card">
<div class="card-hdr" onclick="toggleConcept(${i})">
  <span class="card-title">${c.title}</span>
  <span class="evbadge ${evClass}">${ev}</span>
  <span class="chevron${open?" open":""}">▾</span>
</div>
${open?`<div class="card-body">
  <div class="progress-bar-bg" style="margin-top:12px"><div class="ev-bar ${barClass}"></div></div>
  <p style="font-size:13px;color:var(--text-secondary);line-height:1.6;margin-bottom:10px">${c.summary}</p>
  <div class="section-label">Key points</div>
  <ul class="kp-list">${c.keyPoints.map(p=>`<li class="${p.startsWith("WARN:")?"warn":""}">${p.replace("WARN:","")}</li>`).join("")}</ul>
  <div class="section-label">Clinical implications</div>
  <ul class="kp-list">${c.clinical.map(p=>`<li>${p}</li>`).join("")}</ul>
  ${c.stats.length?`<div class="section-label">Key statistics</div>
  <div>${c.stats.map(s=>`<div class="stat-row">
    <span class="stat-name">${s.o}</span>
    <span class="stat-val">${s.v} <span class="ci-tag">${s.ci}</span></span>
    <span class="stat-dir ${dirClass(s.d)}">${s.d}</span>
  </div>`).join("")}</div>`:""}
  <div class="src-row">Sources: ${c.sources}</div>
</div>`:""}
</div>`;}).join("")}`;
}

function renderVignettes(){
  return`<div class="section-hdr">Clinical vignettes</div>
<div class="section-sub">5 case-based reasoning scenarios. Select any vignette to reveal the discussion.</div>
${vignettes.map((v,i)=>{
const open=openVignette===i;
return`<div class="card">
<div class="card-hdr" onclick="toggleVig(${i})">
  <span class="card-title">${v.title}</span>
  <span class="chevron${open?" open":""}">▾</span>
</div>
${open?`<div class="card-body">
  <div class="section-label">Scenario</div>
  <p style="font-size:13px;color:var(--text-secondary);line-height:1.6;margin-bottom:8px">${v.scenario}</p>
  <div class="vig-q"><strong style="color:var(--text-accent);font-size:11px;text-transform:uppercase;letter-spacing:.06em">Clinical question</strong><br>${v.question}</div>
  <div style="font-size:11px;color:var(--text-muted);margin:6px 0 2px">Framework: ${v.framework}</div>
  <div class="section-label">Discussion</div>
  ${v.points.map(p=>`<div class="vig-disc-item">${p}</div>`).join("")}
  <div class="lesson-box"><strong style="font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--text-success)">Key lesson</strong><br>${v.lesson}</div>
  <div class="pitfall-box"><strong style="font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--text-danger)">Common pitfall</strong><br>${v.pitfall}</div>
</div>`:""}
</div>`;}).join("")}`;
}

function renderEvidence(){
  return`<div class="section-hdr">Evidence tables</div>
<div class="section-sub">Key statistics organised by comparison type. All figures cited directly from source cards.</div>

<div class="card" style="margin-bottom:16px">
<div style="padding:12px 16px;font-weight:500;font-size:13px;border-bottom:0.5px solid var(--border)">Cochrane 2016: midwife-led continuity vs other models (17,674 women, 15 RCTs)</div>
<div style="padding:12px 16px;overflow-x:auto">
<table class="ev-table"><thead><tr><th>Outcome</th><th>RR</th><th>95% CI</th><th>Studies (n)</th><th>Direction</th></tr></thead><tbody>
<tr><td class="tbl-outcome">Regional analgesia</td><td class="tbl-val">0.85</td><td>0.78–0.92</td><td>14 (17,674)</td><td class="dir-down">↓ significant</td></tr>
<tr><td class="tbl-outcome">Instrumental vaginal birth</td><td class="tbl-val">0.90</td><td>0.83–0.97</td><td>13 (17,501)</td><td class="dir-down">↓ significant</td></tr>
<tr><td class="tbl-outcome">Preterm birth (&lt;37 wks)</td><td class="tbl-val">0.76</td><td>0.64–0.91</td><td>8 (13,238)</td><td class="dir-down">↓ significant</td></tr>
<tr><td class="tbl-outcome">All fetal loss + neonatal death</td><td class="tbl-val">0.84</td><td>0.71–0.99</td><td>13 (17,561)</td><td class="dir-down">↓ significant</td></tr>
<tr><td class="tbl-outcome">Spontaneous vaginal birth</td><td class="tbl-val">1.05</td><td>1.03–1.07</td><td>12 (16,687)</td><td class="dir-up" style="color:var(--text-success)">↑ significant</td></tr>
<tr><td class="tbl-outcome">Caesarean section</td><td class="tbl-val">0.92</td><td>0.84–1.00</td><td>14 (17,674)</td><td class="dir-flat">~ NO sig. diff.</td></tr>
<tr><td class="tbl-outcome">Postpartum haemorrhage</td><td class="tbl-val">—</td><td>—</td><td>—</td><td class="dir-flat">~ NO sig. diff.</td></tr>
<tr><td class="tbl-outcome">NICU admission</td><td class="tbl-val">—</td><td>—</td><td>—</td><td class="dir-flat">~ NO sig. diff.</td></tr>
</tbody></table></div></div>

<div class="card" style="margin-bottom:16px">
<div style="padding:12px 16px;font-weight:500;font-size:13px;border-bottom:0.5px solid var(--border)">Souter 2019: midwifery vs obstetrician care, hospital setting (23,100 low-risk births)</div>
<div style="padding:12px 16px;overflow-x:auto">
<table class="ev-table"><thead><tr><th>Outcome</th><th>aRR</th><th>95% CI</th><th>Direction</th></tr></thead><tbody>
<tr><td class="tbl-outcome">C-section (nulliparous)</td><td class="tbl-val">0.68</td><td>0.57–0.82</td><td class="dir-down">↓ ~30%</td></tr>
<tr><td class="tbl-outcome">C-section (multiparous)</td><td class="tbl-val">0.57</td><td>0.36–0.89</td><td class="dir-down">↓ ~40%</td></tr>
<tr><td class="tbl-outcome">Operative vaginal (nulliparous)</td><td class="tbl-val">0.73</td><td>0.57–0.93</td><td class="dir-down">↓ significant</td></tr>
<tr><td class="tbl-outcome">Operative vaginal (multiparous)</td><td class="tbl-val">0.30</td><td>0.14–0.63</td><td class="dir-down">↓ significant</td></tr>
<tr><td class="tbl-outcome" style="color:var(--text-danger)">⚠ Shoulder dystocia (multiparous)</td><td class="tbl-val" style="background:var(--bg-danger);color:var(--text-danger)">1.42</td><td>1.04–1.92</td><td class="dir-up">↑ INCREASED RISK</td></tr>
</tbody></table></div></div>

<div class="card" style="margin-bottom:16px">
<div style="padding:12px 16px;font-weight:500;font-size:13px;border-bottom:0.5px solid var(--border)">McRae 2018: antenatal midwifery vs physician models, low-SES women (57,872 women, Canada)</div>
<div style="padding:12px 16px;overflow-x:auto">
<table class="ev-table"><thead><tr><th>Outcome</th><th>aOR vs GP</th><th>aOR vs OB</th></tr></thead><tbody>
<tr><td class="tbl-outcome">Small for gestational age (SGA)</td><td class="tbl-val">0.71 (0.62–0.82)</td><td class="tbl-val">0.59 (0.50–0.69)</td></tr>
<tr><td class="tbl-outcome">Preterm birth (&lt;37 wks)</td><td class="tbl-val">0.74 (0.63–0.86)</td><td class="tbl-val">0.53 (0.45–0.62)</td></tr>
<tr><td class="tbl-outcome">Low birth weight (&lt;2500g)</td><td class="tbl-val">0.66</td><td class="tbl-val">0.43</td></tr>
</tbody></table></div></div>

<div class="card" style="margin-bottom:16px">
<div style="padding:12px 16px;font-weight:500;font-size:13px;border-bottom:0.5px solid var(--border)">Cambodia health systems strengthening: key metrics (Van Lerberghe 2014, WHO Cambodia 2015)</div>
<div style="padding:12px 16px;overflow-x:auto">
<table class="ev-table"><thead><tr><th>Indicator</th><th>Baseline</th><th>Endpoint</th><th>Change</th></tr></thead><tbody>
<tr><td class="tbl-outcome">MMR (national data)</td><td>432/100k LB (2000)</td><td>206/100k LB (2010)</td><td class="dir-down">↓ 52%</td></tr>
<tr><td class="tbl-outcome">MMR (inter-agency estimate)</td><td>1,200/100k LB (1990)</td><td>170/100k LB (2013)</td><td class="dir-down">↓ 86%</td></tr>
<tr><td class="tbl-outcome">Skilled birth attendance</td><td>32% (2000)</td><td>84% HIS (2013)</td><td class="dir-down" style="color:var(--text-success)">↑ significant</td></tr>
<tr><td class="tbl-outcome">Facility delivery rate</td><td>10% (2000)</td><td>80% HIS (2013)</td><td class="dir-down" style="color:var(--text-success)">↑ significant</td></tr>
<tr><td class="tbl-outcome">ANC 4+ visits</td><td>9% (2000)</td><td>59% (2010)</td><td class="dir-down" style="color:var(--text-success)">↑ significant</td></tr>
<tr><td class="tbl-outcome">BEmONC facilities</td><td>25 (2009)</td><td>96 (2013)</td><td class="dir-down" style="color:var(--text-success)">↑ 3.8×</td></tr>
<tr><td class="tbl-outcome">CEmONC facilities</td><td>19 (2009)</td><td>36 (2013)</td><td class="dir-down" style="color:var(--text-success)">↑ 1.9×</td></tr>
<tr><td class="tbl-outcome">Exclusive breastfeeding (&lt;6 months)</td><td>11% (2000)</td><td>74% (2010)</td><td class="dir-down" style="color:var(--text-success)">↑ significant</td></tr>
<tr><td class="tbl-outcome">Neonatal deaths as % of U5 deaths</td><td>—</td><td>50% by 2010</td><td style="color:var(--text-danger)">⚠ Persistent gap</td></tr>
</tbody></table></div></div>

<div style="font-size:12px;color:var(--text-muted);padding:4px 0">Note: Source 9 (IHME SDG visualization tool) returned 404 — that course URL is broken/retired. The IHME IHME interactive data visuals portal and GBD study (Source 12) are the current active equivalents.</div>`;
}

function renderChecklists(){
  return`<div class="section-hdr">Checklists</div>
<div class="section-sub">Evidence-based clinical assessment tools drawn from the module sources. Check items to track progress.</div>
${checklists.map((cl,ci)=>`<div class="card" style="margin-bottom:16px">
<div style="padding:14px 16px;border-bottom:0.5px solid var(--border)">
  <div style="font-size:14px;font-weight:500">${cl.title}</div>
  <div style="font-size:12px;color:var(--text-muted);margin-top:4px">${cl.subtitle}</div>
</div>
<div style="padding:12px 16px">
${cl.sections.map((s,si)=>`<div class="cl-section">
<div class="cl-section-hdr" onclick="toggleCl(${ci},${si})">${s.title} <span style="float:right">${openClSection[ci][si]?"▾":"▸"}</span></div>
${openClSection[ci][si]?s.items.map((item,ii)=>`<div class="cl-item">
<input type="checkbox" id="cl_${ci}_${si}_${ii}" ${checks[ci+'_'+si+'_'+ii]?"checked":""} onchange="toggleCheck('${ci}_${si}_${ii}')">
<label for="cl_${ci}_${si}_${ii}">${item}</label>
</div>`).join(""):""}
</div>`).join("")}
</div>
</div>`).join("")}`;
}

function renderQuiz(){
  return`<div class="section-hdr">Active recall: 20 questions</div>
<div class="section-sub">Test your retention. Attempt each question mentally before revealing the answer.</div>
${quizData.map((q,i)=>`<div class="quiz-card">
<div class="quiz-num">Question ${i+1} of ${quizData.length}</div>
<div class="quiz-q">${q.q}</div>
<button class="quiz-reveal-btn" onclick="revealQ(${i})">${revealed[i]?"Hide answer":"Reveal answer"}</button>
${revealed[i]?`<div class="quiz-ans">${q.a}</div>`:""}
</div>`).join("")}`;
}

function renderContent(){
  const el=document.getElementById("tab-content");
  if(activeTab==="concepts")el.innerHTML=renderConcepts();
  else if(activeTab==="vignettes")el.innerHTML=renderVignettes();
  else if(activeTab==="evidence")el.innerHTML=renderEvidence();
  else if(activeTab==="checklists")el.innerHTML=renderChecklists();
  else if(activeTab==="quiz")el.innerHTML=renderQuiz();
}

window.switchTab=switchTab;
window.toggleConcept=function(i){openConcept=openConcept===i?null:i;renderContent();};
window.toggleVig=function(i){openVignette=openVignette===i?null:i;renderContent();};
window.revealQ=function(i){revealed[i]=!revealed[i];renderContent();};
window.toggleCl=function(ci,si){openClSection[ci][si]=!openClSection[ci][si];renderContent();};
window.toggleCheck=function(key){checks[key]=!checks[key];};

renderTabs();
renderContent();
</script>
