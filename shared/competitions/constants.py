"""Holds all constants and lookup values."""

# This is the maximum round number from any WSC or GP. It needs to be updated
# if any subsequently-added competition has a higher round number.
MAXIMUM_ROUND = 16

# These were identified partially by hand and partially with a utility
# function using difflib.
WSC_NAME_TO_GP_ID_OVERRIDE = {
    "Zvěřina Jan": "Jan Zverina (Nickless) - Czech Rep.",
    "Jan Zvěřina": "Jan Zverina (Nickless) - Czech Rep.",
    "Demiger Matúš": "Matus Demiger (Nickless) - Slovakia",
    "De Laat Bram": "Bram de Laat (Para) - Netherlands",
    "Bram De Laat": "Bram de Laat (Para) - Netherlands",
    "Hudák Peter": "Peter Hudak (ppeetteerr) - Slovakia",
    "Beenhakker Chiel": "Chiel Beenhakker Beenhakker (bakpao) - Netherlands",
    "Hu Yuxuan": "Hu Yuxuan Hu (huyuxuan) - China",
    "Qiu Suzhe": "Suzhe QIU (ysbg123) - China",
    "Yang Leduo": "Le Duo Yang (Sky Yang) - China",
    "Xie Yifan": "YiFan Xie (evan_xie) - China",
    "Prasanna Venkatesh Seshadri": "Prasanna Seshadri (prasanna16391) - India",
    "Yu Tianxiang": "TianXiang Yu Yu (Yutx) - China",
    "Kishore Kumar Sridharan": "Kishore Sridharan (kishy72) - India",
    "Huang Xiaowei": "Xiao Wei Huang (xiao01wei) - China",
    "Highryll Cj Tan": "CJ Tan (hetan) - Philippines",
    "Neil Gary Zussman": "Neil Zussman (Nilz) - UK",
    "Kartik Reddy Mogiligundla": "Kartik Reddy (Nickless) - India",
    "Zoltán Horváth": "Zoltan Horvath (Valezius) - Hungary",
    "Thomas Collyer": "Tom Collyer (Nickless) - UK",
    "Hong Seonghwa": "SeongHwa Hong (Nickless) - Korea, South",
    "Guenther Susanne": "Susanne Günther (zuzanina) - Germany",
    "Schuckert Eva-Maria": "Eva Schuckert (Nickless) - Austria",
    "Jaipal Reddy Mogiligundla": "Jaipal Reddy (mjaipal) - India",
    "Olga Diaz Moruno": "Olga Diaz (Nickless) - Spain",
    "Özgün Onur Özdemir": "Özgün Onur ÖZDEMİR (Nickless) - Turkey",
    "Terveer Sara Karina": "Sara Terveer (Nickless) - Germany",
    "Roger Peter Kohler": "Roger Kohler (ropeko) - Switzerland",
    "Plassmann Volker Conrad": "Volker Plassmann (Nickless) - Germany",
    "Jin Sungwon": "Sung-Won Jin (swj219) - Korea, South",
    "David Mcneill": "David McNeill (Nickless) - UK",
    "Keisu Okuma": "Keisui Okuma (Nickless) - Japan",
    "Schukert Eva": "Eva Schuckert (Nickless) - Austria",
    "Piibeleht Tiit Hendrik": "Tiit Hendrik Piibeleht (Tiiduke) - Estonia",
    "Vesna Jovanović": "Vesna Jovanovic (vesnasta) - Serbia",
    "Michaël Genier": "Michael Genier (LoHoX) - Switzerland",
    "Poulsen Henning Kalsgaard": "Henning Kalsgaard Poulsen (Kalsgaard) - Denmark",
    "Buyukkale Yunus Emre": "Yunus Emre Büyükkale (ynus) - Turkey",
    "Mladen Meštrović": "Mladen Mestrovic (mestar) - Croatia",
    "Brütsch Christof": "Christof Bruetsch (chrishy) - Switzerland",
    "Grigoļunovičs Andrejs": "Andrew Grigolunovich (AGCFA) - Latvia",
    "Jeļena Balanova": "Jelena Balanova (Nickless) - Latvia",
    'Alberto Filippini': "alberto filippini (albfilip) - Italy",
    "Filippini Alberto": "alberto filippini (albfilip) - Italy",
    'Sara Martin': "sara martin (Nickless) - Italy",
    "Ekaterina Nuzhdina": "Ekaterina Nuzdina (Nickless) - Russia",
    "Ashford Zoë": "Zoe Ashford (Zo_Ashford) - UK",
    "Richard Demsyn-Jones": "Richard Jones (rdj) - Canada",
    "Stackhouse Shawn": "S S (Nickless) - Canada",
    "Kuber Karthik": "Karthik K (krthk) - Canada",
    "Pranav Kamesh Sivakumar": "Pranav Kamesh (pranavmanu) - India",
    "Zoran Tanasić": "Zoran Tanasic (zorant) - Serbia",
    "Swaroop Srinivasrao Guggilam": "swaroop guggilam (swaroop2011) - India",
    "Nicole Schädel": "Nicole Schaedel (Mira) - Germany",
    "Karel Štěrba": "Karel Sterba (chlien) - Czech Rep.",
    "Jana Hanzelková": "Jana Hanzelkova (Tydela) - Czech Rep.",
    "Stefano Forcolin": "stefano forcolin (sf2l) - Italy",
    "Veronika Koľveková": "Veronika Kolvekova (Nickless) - Slovakia",
    "Kosei Yoshimori": "kosei yoshimori (simorin) - Japan",
    "Tomáš Krejčí": "Tom Krejčí (tierra) - Czech Rep.",
    "Robert Beärda": "Robert Bearda (Nickless) - Netherlands",
    "Raul Kačírek": "Raul Kacirek (Caca) - Czech Rep.",
    "Michele Bongiorno": "michele bongiorno (wiseman89) - Italy",
    "Daniele Colnaghi": "daniele colnaghi (SAYAN) - Italy",
    "Miroslav Šalaga": "Miroslav Salaga (macko) - Slovakia",
    "Jiwon Seo": "jiwon seo (Nickless) - Korea, South",
    "Gabriela Jaselská": "Gabriela Jaselska (Nickless) - Slovakia",
    "Blanka Lehotská": "Blanka Lehotska (hypsugo) - Slovakia",
    "Ján Farkaš": "Jan Farkas (slovak) - Slovakia",
    "Paolo Tivano": "paolo tivano (flin68) - Italy",
    "Iliana-Eleftheria Gounalaki": "Iliana Gounalaki (gounil) - Greece",
    "Peter Hornák": "Peter Hornak (petho) - Slovakia",
    "Pierdante Lanzavecchia": "Pierdante LANZAVECCHIA (Pierdante) - Italy",
    "Martin Fundárek": "Martin Fundarek (Nickless) - Slovakia",
    "Hyuksun Kwon": "hyuk sun Kwon (dolgore63) - Korea, South",
    "Aleš Založnik": "Ales Zaloznik (Aleš) - Slovenia",
    "Heungchul (John) Park": "Heungchul John Park (puzzlerepublic) - Korea, South",
    "Ľuboš Hyžák": "Lubos Hyzak (Nickless) - Slovakia",
    "Sunseong Kwon": "sunseong kwon (bomulsum) - Korea, South",
    "Saejoon Jang": "Sae Joon Jang (Nickless) - Korea, South",
    "Park Heungchul": "Heungchul John Park (puzzlerepublic) - Korea, South",
    "Mestrovic Davor": "Mladen Mestrovic (mestar) - Croatia",
    "Jan Novotny": "Jan Novotný (KrtekHonza) - Czech Rep.",
    "Klara Vytiskova": "Klára Vytisková (QKV) - Czech Rep.",
    "Hatice Esra Aydemir": "esra aydemir (aras) - Turkey",
    "Natalia Chanova": "Natália Chanová (natalka) - Slovakia",
    "Pavel Jaselsky": "Pavel Jaselský (pali7) - Slovakia",
    "Jana Vodickova": "Jana Vodičková (Janka) - Czech Rep.",
    "Hemant Kumar Malani": "Hemant Kr Malani (Nickless) - India",
    "Ralph Joshua P. Sarrosa": "Ralph Joshua Sarrosa (Nickless) - Philippines",
    "Cedomir Milanovic": "cedomir milanovic (rimodech) - Serbia",
    "Yuki Yamamoto": "Yuuki Yamamoto (brend) - Japan",
    "Deyan Razsadov ": "Deyan Razsadov (Deyan) - Bulgaria",
    "Svilen Dyakovski ": "Svilen Dyakovski (sdyakovski) - Bulgaria",
    "Charlotte Kroll": "Charlotte Anna Friederike Kroll (char.krol) - Germany",
    "John Joseph Dj Gabata": "John Joseph Gabata (Joseph) - Philippines",
    "Lenson Mithun Savio Andrade": "Lenson Andrade (lenson) - India",
    "Zdenek Vodicka": "Zdeněk Vodička (Voda) - Czech Rep.",
    "Aleksey Laptiev": "Alexey Laptiev (Kukuruza) - Russia",
    "Borislav Ilevski ": "Borislav Ilevski Ilevski (ilevski) - Bulgaria",
    "Arvid Jurgen Baars": "Arvid Baars (Eisbaer) - Netherlands",
    "Kulli Laks-Vahemae": "Külli Laks Vahemäe (Volvo) - Estonia",
    "Ondrousek Jakub": "Jakub Ondroušek (Nickless) - Czech Rep.",
    "David Tyler Jones": "David Jones (WMathie) - Canada",
    "Sridharan Kishore Kumar": "Kishore Sridharan (kishy72) - India",
    "Strozak Tomasz": "Tomasz Stróżak (strozo) - Poland",
    "Kadlecık Pavel": "Pavel Kadlečík (kousek-nebe) - Czech Rep.",
    "Gyimesi Zoltan": "Gyimesi Zoltán (Hunsudoku) - Hungary",
    "Meyapin Yannic": "Meyapin Yannick (Nickless) - France",
    "Zentgraf Jorg": "Jörg Zentgraf (Nickless) - Germany",
    "Mccaughan Emma": "Emma McCaughan (Emma) - UK",
    "Baines David": "Dave Baines (StandupCanada) - Canada",
    "Seung-Jae Kwak": "Seungjae Kwak (Kwaka) - Korea, South",
    "Jason Zuffraneiri": "Jason Zuffranieri (Ziti) - USA",
    "Štefan Gašpár": "Stefan Gaspar (pista) - Slovakia",
    "Gabriel Gan Rong De": "Gabriel Gan (rongde96) - Singapore",
    "Diana Škrhová": "Diana Skrhova (Anaid) - Slovakia",
    "Čedomir Milanović": "cedomir milanovic (rimodech) - Serbia",
    "Michael Moßhammer": "Michael Mosshammer (moss) - Austria",
    "Serkan Yürekli": "Serkan Yurekli (Nickless) - Turkey",
    "René Gilhuijs": "Rene Gilhuijs (RCG) - Netherlands",
    "Hugo Van Rooijen": "Hugo van Rooijen (Nickless) - Netherlands",
    "Heung-Chul(John) Park": "Heungchul John Park (puzzlerepublic) - Korea, South",
    "Ivana Štiptová": "Ivana Stiptova (tilansia) - Slovakia",
    "Frédéric Prevot": "Frédéric PREVOT (Ours Blanc) - France",
    "Swaroop Guggilam": "swaroop guggilam (swaroop2011) - India",
    "Veronika Macku": "Veronika Macků (Pherenike) - Czech Rep.",
    "Raoul Kačírek": "Raul Kacirek (Caca) - Czech Rep.",
    "Olga Díaz Moruno": "Olga Diaz (Nickless) - Spain",
    "Jouni Juhani Särkijärvi": "Jouni Särkijärvi (peluri) - Finland",
    "Beri Kohen Behar": "Beri Kohen (BERI) - Turkey",
    "Iliana-Eleytheria Gounalaki": "Iliana Gounalaki (gounil) - Greece",
    "Borislav Ilevski": "Borislav Ilevski Ilevski (ilevski) - Bulgaria",
    "Galina Titova": "Galya Titova (galka) - Bulgaria",
    "John Hc Park": "John HC Park (puzzlerepublic) - Korea, South",
    "Nikola Živanovic": "Nikola Zivanovic (NikolaZ) - Serbia",
    "Jana Brízová": "Jana Břízová (tojejedno) - Czech Rep.",
    "Fred Stalder": "Frédéric Stalder (Fred76) - Switzerland",
    "Pavel Kadlecík": "Pavel Kadlečík (kousek-nebe) - Czech Rep.",
    "Petra Cicová": "Petra Čičová (Nickless) - Czech Rep.",
    "Pawel Rachel": "Paweł Rachel (rachelinator) - Poland",
    "Jirí Hrdina": "Jiri Hrdina (jhrdina) - Czech Rep.",
    "Tomasz Strózak": "Tomasz Stróżak (strozo) - Poland",
    "Kerstin Woege": "Kerstin Wöge (Nickless) - Germany",
    "Joerg Zentgraf": "Jörg Zentgraf (Nickless) - Germany",
    "Laurent Saillot": "Laurent SAILLOT (LauLot57) - France",
    "Nikola Živanović": "Nikola Zivanovic (NikolaZ) - Serbia",
    "Wilbert Zwart": "Wilbert Zwart Wilbert (Space_wuppie) - Netherlands",
    "Zoran Таnasić": "Zoran Tanasic (zorant) - Serbia",
    "Jiří Hrdina": "Jiri Hrdina (jhrdina) - Czech Rep.",
    "Gülce Senem Özkütük Yürekli": "Gülçe Özkütük (Nickless) - Turkey",
    "Paweł Kępczyński": "Pawel Kepczynski (pafcio) - Poland",
    "Łukasz Kalinowski": "Lukasz Kalinowski (Nickless) - Poland",
    "Christiana Karakigianou": "Kristiana Karakigianou (farmatwnzwwn) - Greece",
    "Daisuke Takei": "Daisuke TAKEI (hotondo) - Japan",
    "Štefan Gyürki": "Stefan Gyürki (gypista) - Slovakia",
    "William Blatt": "Will Blatt (willwc) - USA",
    "Henning Poulsen": "Henning Kalsgaard Poulsen (Kalsgaard) - Denmark",
    "Tammy Mcleod": "Tammy McLeod (Nickless) - USA",
    "Recep Gül": "Recep GÜL (Nickless) - Turkey",
    "Mike Aisen": "Michael Aisen (maisen) - Canada",
    "Jan Zvérina": "Jan Zverina (Nickless) - Czech Rep.",
    "Jana Novotna": "Jana Novotná (tojejedno) - Czech Rep.",
    "Pavel Kadlecik": "Pavel Kadlečík (kousek-nebe) - Czech Rep.",
    "Andrej Plastiak": "Andrej Plaštiak (Nickless) - Slovakia",
    "Petra Cigova": "Petra Čičová (Nickless) - Czech Rep.",
    "Kerstin Wége": "Kerstin Wöge (Nickless) - Germany",
    "Gulia Franceschini": "Giulia Franceschini (iris) - Italy",
    "Przemystaw Debiak": "Przemysław Dębiak (Psyho) - Poland",
    "Karel Stérba": "Karel Sterba (chlien) - Czech Rep.",
    "Pranav Kamesh Sivak": "Pranav Kamesh (pranavmanu) - India",
    "Raul Ka¢Éirek": "Raul Kacirek (Caca) - Czech Rep.",
    "Akash Doulani": "akash doulani (akashdoulani78) - India",
    "Marek Kasar": "Marek Kasár (markas999) - Slovakia",
    "Maarit Ryynanen": "Maarit Ryynänen (Nickless) - Finland",
    "Ulla Elsila": "Ulla Elsilä (UllaE) - Finland",
    "Pawel Kepezynski": "Pawel Kepczynski (pafcio) - Poland",
    "Ashish Kumar": "ashish kumar (ashaash11ash) - India",
    "Gerda Nador": "Gerda Nádor (ingalili) - Hungary",
    "Gyérgy Herke": "György Herke (Gyuszi13) - Hungary",
    "Boglar Major": "Boglár Major (bmajor) - Hungary",
    "Fanni Pipé": "Fanni Pipó (Nickless) - Hungary",
    "Lucia Ondovéikovd": "Lucka Ondovcikova (Nickless) - Slovakia",
    "Jouni Sarkijarvi": "Jouni Särkijärvi (peluri) - Finland",
    "Tomasz Stanezak": "Tomasz Stańczak (stan) - Poland",
    "Claudio Toffon": "claudio toffon (claudio62) - Italy",
    "Evgenii Bekishev": "Evgeniy Bekishev (Eugene) - Russia",
    "Pranav Kamesh S": "Pranav Kamesh (pranavmanu) - India",
    "Adam Šuráň": "Adam Suran (hjkl18) - Czech Rep.",
    "Sunghwa Hong": "SeongHwa Hong (Nickless) - Korea, South",
    "Jaipal Reddy M": "Jaipal Reddy (mjaipal) - India",
    "Edouard Lebeau": "Édouard Lebeau (mandourin) - France",
    "Rick Uppelschoten": "Kaari Helstein (pisipaha) - Estonia",
    "Tiit-Hendrik Piibeleht": "Tiit Hendrik Piibeleht (Tiiduke) - Estonia",
    "Martina Prinerova": "Martina Prinerová (eifel_mp) - Slovakia",
    "Radoslav Bochev": "Rado Bo4ev (tres4o) - Bulgaria",
    "Dávid Braun": "David Braun (Braunka625) - Hungary",
    "Michaele Bongiorno": "michele bongiorno (wiseman89) - Italy",
    "Christof Brutsch": "Christof Bruetsch (chrishy) - Switzerland",
    "Külli Laks-Vahemäe": "Külli Laks Vahemäe (Volvo) - Estonia",
    "Iliana - Eleftheria Gounalaki": "Iliana Gounalaki (gounil) - Greece",
    "Zdeňka Pácalová": "Zdenka Pácalová (zdenkap) - Czech Rep.",
    "Kaja Sõstra": "Kaja Sostra (Nickless) - Estonia",
}

GP_PLAYOFF_RESULTS = {
    2014: {
        1: "Tiit Vunk (TiiT) - Estonia",
        2: "Kota Morinishi (Kota) - Japan",
        3: "Bastien Vial-Jaime (Nickless) - France",
        4: "Seungjae Kwak (Kwaka) - Korea, South",
        5: "Hideaki Jo (Nickless) - Japan",
        6: "Michael Ley (misko) - Germany",
        7: "Nikola Zivanovic (NikolaZ) - Serbia",
        8: "Ulrich Voigt (uvo) - Germany",
        9: "Rishi Puri (purifire) - India",
        10: "Timothy Doyle (Timothy) - France",
    },
    2015: {
        1: "Kota Morinishi (Kota) - Japan",
        2: "Timothy Doyle (Timothy) - France",
        3: "Tiit Vunk (TiiT) - Estonia",
        4: "Bastien Vial-Jaime (Nickless) - France",
        5: "Jakub Ondroušek (Nickless) - Czech Rep.",
        6: "Prasanna Seshadri (prasanna16391) - India",
        7: "Rishi Puri (purifire) - India",
        8: "Seungjae Kwak (Kwaka) - Korea, South",
        9: "Vincent Bertrand (Nickless) - Belgium",
        10: "Frédéric Stalder (Fred76) - Switzerland",
    },
    2016: {
        1: "Tiit Vunk (TiiT) - Estonia",
        2: "Kota Morinishi (Kota) - Japan",
        3: "Hideaki Jo (Nickless) - Japan",
        4: "Seungjae Kwak (Kwaka) - Korea, South",
        5: "Prasanna Seshadri (prasanna16391) - India",
        6: "Michael Ley (misko) - Germany",
        7: "Tantan Dai (SERENE) - China",
        8: "Jan Novotný (KrtekHonza) - Czech Rep.",
        9: "Matus Demiger (Nickless) - Slovakia",
        10: "Jan Zverina (Nickless) - Czech Rep.",
    },
    2017: {
        1: "Seungjae Kwak (Kwaka) - Korea, South",
        2: "Tantan Dai (SERENE) - China",
        3: "Tiit Vunk (TiiT) - Estonia",
        4: "Sinchai Rungsangrattanakul (sinchai4547) - Thailand",
        5: "Hideaki Jo (Nickless) - Japan",
        6: "Kota Morinishi (Kota) - Japan",
        7: "Takuya Sugimoto (sugitakukun) - Japan",
        8: "David Jones (WMathie) - Canada",
        9: "Michael Ley (misko) - Germany",
        10: "Thomas Snyder (DrSudoku) - USA",
    },
    2018: {
        1: "Jakub Ondroušek (Nickless) - Czech Rep.",
        2: "Kota Morinishi (Kota) - Japan",
        3: "Tantan Dai (SERENE) - China",
        4: "Seungjae Kwak (Kwaka) - Korea, South",
        5: "Tiit Vunk (TiiT) - Estonia",
        6: "Michael Ley (misko) - Germany",
        7: "Jan Mrozowski (janoslaw) - Poland",
        8: "Takuya Sugimoto (sugitakukun) - Japan",
        9: "Sinchai Rungsangrattanakul (sinchai4547) - Thailand",
        10: "Cheran Sun (青清晴情) - China",
    },
    2019: {
        1: "Jakub Ondroušek (Nickless) - Czech Rep.",
        2: "Bastien Vial-Jaime (Nickless) - France",
        3: "Kota Morinishi (Kota) - Japan",
        4: "Tantan Dai (SERENE) - China",
        5: "Jan Mrozowski (janoslaw) - Poland",
        6: "Seungjae Kwak (Kwaka) - Korea, South",
        7: "Tiit Vunk (TiiT) - Estonia",
        8: "Timothy Doyle (Timothy) - France",
        9: "Hideaki Jo (Nickless) - Japan",
        10: "Takuya Sugimoto (sugitakukun) - Japan",
    },
    2020: {
        1: "Tiit Vunk (TiiT) - Estonia",
        2: "Tantan Dai (SERENE) - China",
        3: "Jakub Ondroušek (Nickless) - Czech Rep.",
        4: "Kota Morinishi (Kota) - Japan",
        5: "Bastien Vial-Jaime (Nickless) - France",
        6: "Ken Endo (EKBM) - Japan",
        7: "Seungjae Kwak (Kwaka) - Korea, South",
        8: "Weifan Wang (qw014052) - China",
        9: "Hideaki Jo (Nickless) - Japan",
        10: "Takuya Sugimoto (sugitakukun) - Japan",
    },
    2024: {
        1: "Tiit Vunk (TiiT) - Estonia",
        2: "Tantan Dai (SERENE) - China",
        3: "Hu Yuxuan Hu (huyuxuan) - China",
        4: "Seungjae Kwak (Kwaka) - Korea, South",
        5: "Letian Ming (Mike) - China",
        6: "Ken Endo (EKBM) - Japan",
        7: "Suzhe QIU (ysbg123) - China",
        8: "Cheran Sun (青清晴情) - China",
        9: "Le Duo Yang (Sky Yang) - China",
        10: "Kota Morinishi (Kota) - Japan",
        11: "David Jones (WMathie) - Canada",
        12: "Sinchai Rungsangrattanakul (sinchai4547) - Thailand",
        13: "Takuya Sugimoto (sugitakukun) - Japan",
        14: "Martin Merker (MaM) - Germany",
        15: "Kishore Sridharan (kishy72) - India",
    }
}
