# Fact-check of the drafted pages (slides 7 and 12 to 15), 2026-10-05

Charlie asked for research to confirm the assertions on the pages Claude drafted. Each line gives
the claim as drafted, the finding, the source, and what changed on the slide. Data pulled through
the Bloomberg Desktop API is in `analysis/data/` with its tickers; web sources are linked.

## Slide 14, Greece versus France

| Claim | Finding | Source | Slide |
|---|---|---|---|
| Greece lost market access in 2010 | Downgraded to junk in April 2010, requested EU/IMF aid on 23 April, €110bn programme agreed 2 May 2010; first bond sale since then on 10 April 2014 (€3bn 5-year at 4.75%) | [Wikipedia, First Economic Adjustment Programme](https://en.wikipedia.org/wiki/First_Economic_Adjustment_Programme_for_Greece); [Global News, April 2014](https://globalnews.ca/news/1257125/back-from-cold-greece-announces-market-return/) | confirmed; "lost, April 2010; regained April 2014" |
| 53.5% nominal haircut, PSI March 2012 | 97% of eligible bonds (€197bn of €205bn) exchanged, 53.5% nominal haircut, about €107bn of debt relief; new bonds 31.5% of face plus 15% in EFSF bills | [ESM](https://www.esm.europa.eu/content/what-was-private-sector-debt-restructuring-march-2012); [RBA, May 2012](https://www.rba.gov.au/publications/smp/2012/may/box-b.html) | confirmed |
| Greece "about 2% of euro-area output" | 2.0% in 2011 (Eurostat nominal GDP, EUACGR / EUACEZ) | `analysis/fiscal.py` | now computed |
| France "second-largest economy" | 18.7% of euro-area GDP in 2025, second to Germany at 28.4%; Italy 14.2%, Spain 10.6% | `analysis/fiscal.py` | now computed and stated |
| Greece debt 175% of GDP in 2011 | 175.1% (Eurostat) | `analysis/fiscal.py` | confirmed |
| No legal route out of the euro short of leaving the EU; RN dropped the idea after 2017 | RN made euro exit a flagship proposal in 2012 and 2017, abandoned it after the 2017 debate; the 2022 programme is reform from within; in September 2026 Le Pen proposes referendums on other subjects but not on EU membership | [Public Sénat](https://www.publicsenat.fr/article/politique/sur-l-europe-marine-le-pen-a-t-elle-vraiment-change-202482); [Euronews, 17 Sept 2026](https://fr.euronews.com/my-europe/2026/09/17/marine-le-pen-veut-elle-ou-non-organiser-un-referendum-sur-le-frexit-si-elle-est-elue) | confirmed; the legal point (Article 50 is the only exit mechanism) is treaty text, not sourced here |

## Slide 15, the interventions

| Event | Finding | Source |
|---|---|---|
| SMP, May 2010 | decided 9 May, announced 10 May 2010; expired 6 September 2012 | [Yale Program on Financial Stability](https://newbagehot.yale.edu/docs/european-central-bank-securities-markets-programme) |
| 3-year LTROs, December 2011 | announced 8 December 2011; €489bn allotted 22 December 2011, €530bn on 29 February 2012 | [Yale PFS](https://newbagehot.yale.edu/docs/european-central-bank-three-year-long-term-refinancing-operations) |
| OMT | announced 2 August 2012, framework published 6 September 2012; never activated | [Wikipedia, OMT](https://en.wikipedia.org/wiki/Outright_Monetary_Transactions) |
| "Whatever it takes" | 26 July 2012, Draghi in London; not separately sourced here, the date is the ECB's own record | ECB speech archive |
| TPI | approved 21 July 2022 | [ECB press conference, 21 July 2022](https://www.ecb.europa.eu/press/pressconf/2022/html/ecb.is220721~51ef267c68.en.html) |
| APP, January 2015; PEPP, March 2020 | ECB press releases of 22 January 2015 and 18 March 2020; not re-fetched today | ECB |

The slide's dates stand. The table's "effect" column is editorial and says so in the edits log.

## Slide 12, the fiscal situation

| Claim | Finding | Source | Slide |
|---|---|---|---|
| Deficit −5.1%, debt 115.6%, net interest 2.1% of GDP, 2025 | Eurostat and OECD via Bloomberg | `analysis/fiscal.py` | confirmed |
| Ratings S&P A+, Moody's Aa3, Fitch A+ | Fitch cut to A+ in September 2025; S&P cut AA- to A+ on 17 October 2025, stable; Moody's Aa3 stable; S&P had put AA- on negative outlook in late February 2025 | [European Business Magazine](https://europeanbusinessmagazine.com/sp-global-ratings-decision-to-cut-frances-sovereign-credit-rating-focusing-on-the-causes-implications-and-outlook/); [eNCA, March 2025](https://www.enca.com/business/sp-keeps-french-debt-rating-revises-outlook-down); Bloomberg reference fields today | dates added |
| "Each notch moves France further from the AA bucket that many mandates are written around" | an assertion with no source found | — | replaced with the fact: two of the three agencies now rate France below the AA category |

## Slide 13, politics (as of early October 2026)

| Claim | Finding | Source | Slide |
|---|---|---|---|
| Hung Assembly since June 2024; governments fall on budgets | confirmed; the Assembly splits between the RN, the New Popular Front and the centre-right; the 2027 budget fight "threatens to topple another government" | [CNBC, 24 Sept 2026](https://www.cnbc.com/2026/09/24/france-budget-debt-deficit-government.html) (headline; page blocked to fetch) | kept |
| Current government and budget | Prime Minister Sébastien Lecornu presented the 2027 budget to the Council of Ministers on 1 October 2026: €54bn of consolidation including €43bn of new measures, a public-sector pay freeze, a 5% deficit target; to the Assembly by 6 October | [France 24, 1 Oct 2026](https://www.france24.com/en/france/20261001-french-pm-to-present-belt-tightening-2027-budget-including-frozen-wages-and-new-taxes); [Eurasia Business News](https://eurasiabusinessnews.com/2026/10/01/french-budget-2027-government-unveils-e54-billion-fiscal-recovery-plan/) | added |
| Election in spring 2027 | April 2027 | [UK in a Changing Europe, June 2026](https://ukandeu.ac.uk/frances-2027-presidential-race-a-new-transitional-election/) | kept |
| The far right leads the polls | **Corrected after Charlie's challenge.** On 7 July 2026 the Paris Court of Appeal upheld Le Pen's conviction but cut the ineligibility to 45 months with 30 suspended, 15 months effective, which ends before the election; she declared her candidacy the same day ("there is no longer any scenario in which I could not run"); Bardella renounced the nomination and campaigns with her as a possible prime minister. Her Cassation appeal suspends the sentence and does not bar the candidacy. Election dates: 18 April and 2 May 2027. The June 2026 source first used predated the ruling. | [CNN, 7 July 2026](https://www.cnn.com/2026/07/07/europe/marine-le-pen-france-court-ruling-intl); [France 24, 8 July 2026](https://www.france24.com/fr/france/20260708-marine-le-pen-candidate-en-2027-un-choix-dynastique-du-rn-qui-%C3%A9clipse-jordan-bardella); [franceinfo](https://www.franceinfo.fr/politique/front-national/affaire-des-assistants-fn-au-parlement-europeen/il-va-accepter-sans-probleme-la-decision-de-marine-le-pen-comment-jordan-bardella-et-la-candidate-du-rn-vont-ils-faire-campagne-en-binome-en-2027_8098388.html); [Wikipedia, 2027 election](https://en.wikipedia.org/wiki/2027_French_presidential_election) | Le Pen named as candidate and leader; Bardella stood aside; dates added |
| RN: lower pension age | With Le Pen the candidate, the return to retirement at 62 stays in the programme (Bardella's earlier signal to drop it is moot) | as above | stated as her position |
| LFI leader floats cancelling central-bank-held debt | Mélenchon revived in August 2026 his 2022 proposal to cancel the roughly 18% of French debt held by the Banque de France; Lagarde called it a clear treaty violation on 10 September 2026 | [Euronews, 11 Sept 2026](https://www.euronews.com/my-europe/2026/09/11/ecb-chief-christine-lagarde-rejects-melenchons-debt-cancellation-proposal); [The Star / Reuters, 26 Aug 2026](https://www.thestar.com.my/news/world/2026/08/26/hard-left-presidential-candidate039s-plan-to-cancel-french-debt-sparks-backlash) | dates and the 18% added |

## Slide 10, the footnote on local-currency defaults

Russia announced on 17 August 1998 a forced restructuring of its rouble-denominated GKO bills and
OFZ bonds and halted payment on rouble debt, alongside the devaluation
([Wikipedia](https://en.wikipedia.org/wiki/1998_Russian_financial_crisis); [GKO](https://en.wikipedia.org/wiki/GKO)).
Confirmed as a local-currency default by a sovereign with its own currency.

## Slide 7, drafted after this check

Numbers on it: the fiscal figures above; the 5-year France spread's move over the last ten trading
days and the last year, and the 5-year swap rate against a year ago, from `analysis/spread_history.py`
("moves"); the political events above.

## Slide 13 (round 11, 2026-10-07): why no exit or default, Charlie's text

| Claim | Finding | Source | Slide |
|---|---|---|---|
| "Moving the retirement age to [ ] would fix the problem for a decade or more" | The Cour des comptes' report of 20 February 2025: pension-system surplus EUR 8.5bn in 2023, deficit EUR 6.6bn in 2024, EUR 14.6bn projected for 2035; raising the legal age to 65 would save up to EUR 8.4bn by 2035. That covers the pension system's own deficit; it is about 0.3% of GDP against a general deficit of 5.1% of GDP in 2025, so it does not fix the general deficit. | [previssima.fr on the Cour des comptes report](https://www.previssima.fr/actualite/systeme-de-retraite-francais-le-rapport-choc-de-la-cour-des-comptes.html); [Connexion France on the COR](https://www.connexionfrance.com/magazine/people-must-work-until-66-by-2033-to-save-frances-pension-system/749026) | bracket filled with 65 and the figures; the slide says "the pension system's own deficit"; the footnote states the general deficit is a separate matter |
| "France is too big to fail, with 19% of euro-area output" | 18.7% of euro-area nominal GDP in 2025, Eurostat via Bloomberg | `analysis/fiscal.py` | computed, shown as 19% |
| "Political integration ... changed in 2012, when they effectively socialized their collective debt" | Charlie's judgement. The ESM treaty entered into force on 27 September 2012; OMT was announced on 6 September 2012. | ESM, ECB | kept as written; dates in the footnote |
| ESM, OMT, TPI since 2022 | TPI announced 21 July 2022 | ECB | kept |
| The far right dropped euro exit after 2017 | confirmed in round 8 | see slide 14 (round 6) above | kept |

## Slide 7 (round 11): the ratings downgrade among the triggers

| Claim | Finding | Source | Slide |
|---|---|---|---|
| "a Scope downgrade" (from Political Alpha, 5 Oct 2026: "Scope Ratings downgraded France last week") | Scope cut France to A+ from AA- on 18 September 2026, outlook stable, level with Fitch and S&P; Morningstar DBRS moved its AA to a negative outlook the same week | [Bloomberg, 18 Sept 2026](https://www.bloomberg.com/news/articles/2026-09-18/france-s-credit-rating-downgraded-to-a-from-aa-at-scope); [Newsquawk on DBRS](https://www.newsquawk.com/headlines/dbrs-lowers-french-outlook-to-negative-affirms-aa-ratings) | reworded to "a ratings downgrade" at Charlie's request; detail in `third_party_facts` |
