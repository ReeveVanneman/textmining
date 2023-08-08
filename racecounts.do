* racecounts.do
*	input is code-level ("Census") file, collapses to doc-level file
*	7 equivalents for black: African American, Negro, nonwhite, black, colored, minority, of color
*		last 4 terms require disambiguation
*	black and white, black and brown also have separate codes
*		"black and white" requires disambiguation (e.g., black and white photograph)
*		"black and brown" almost always signifies race
*	this stata program is the 2nd (& last) step in disambiguating the ambiguous terms
*		the previous python program sorted each of the 7 terms and two trigrams into:
*			included: about people based on adjacent word(s) in the sentence.
*			excluded: not about people based on the adjacent word(s)
*			ambiguous: adjacent words do not disambiguate the term
*	the "final" measures of race, black, and white disambiguate those remaining ambiguous tokens
*		by seeing if there are other race, black, or white tokens in the entire text
*		bplusrace (black), racebplus (race)
*	if the document includes other racial issues, an ambiguous black etc. is coded as about people
*		if no other racial issues, an ambiguous black etc. is coded as not about people
*	probably not needed for white and black, but it might be useful for other teerms to disambiguate:
*		before checking for themes in the entire text, check for themes in just the sentence witht the code
*		especially if there are "excluding" themes as well as "including" themes, it would be good to start with the immediate sentnece
*			e.g., poor could be financial or a performance
*			e.g., professional could be a middle class occupation, or a distinction from amateur athletes.
*				if a text had both excluding and including themes, the immediate sentence would be decisive
*					but how to analyze just that sentence?
*
* todo: ethnicity v race


/*
ybplusany
	ybplusrace	
		yblackyes,ynegro,ynonwhiite,yminorityyes, yofcolorrace, ycoloredrace= all tokens identified as ~Black from Python
		yblackambig= blackarace
			blackarace= ambiguous black and racial issue in text
			yblackambignot= ambiguous black  but no racial issues in text
	blacknonracial	
		yblacknot= blackexclude
		also blackambignot from yblackambig
yblackany		
	blackracial	
		yblackyes= blackinclude
		yblackambig= blackarace
			blackarace= ambiguous black and racial issue in text
			yblackambignot= ambiguous black  but no racial issues in text
	blacknonracial	
		yblacknot= blackexclude
		also blackambignot from yblackambig
AfricanAmerican		
Negro		
Nonwhite		
Minority		
	minorityracial	
	minorityno	
Ofcolor		
	ofcolorracial	
	ofcolorno	
Colored		
	coloredracial	
	coloredno	
		
	BlackPlus	
		Otherx
*/

set more off

* checking: ambiguous and noncodes not dropped
tab occ2010 if occ2010>=31900
	*drop if occ2010>=31900

duplicates report article  occ2010
sort article occ2010
	* count #codes for each article:
	by article: gen Noccs= _N
	by article: gen nocc= _n
	summarize Noccs if nocc==1, detail
		drop Noccs nocc

recode plurals (1/max=1), gen(yplurals)
	label define yplurals 0 "no plurals 0" 1 "1+plurals 1", modify
	label values yplurals yplurals

tab occ2010 if (occ2010>11200 & occ2010<11300) | (occ2010>15000 & occ2010<15300) | (occ2010>=17000 & occ2010<17409)


* End of Document marker
gen documents= mentions if occ2010==0
	replace documents=0 if occ2010 != 0
	label variable documents "0 End of Documents"
		tab documents, missing
	*drop if occ2010==0
	*drop documents
/*
 "15000": "Minority, allocated",
 "15001": "Minorities, plural",
 "15002": "Minority, coded",
 "15003": "Minority community",
 "15004": "Minority neighborhood",
 "15005": "Minority business",
 "15006": "Minority politics",
 "15008": "Minority ambiguous,check next",
 "15009": "Minority ambiguous,check text",
 "15010": "Negro",
 "15011": "Negroes, plural",
 "15013": "Negro community",
 "15014": "Negro neighborhood",
 "15015": "Negro business",
 "15016": "Negro politics",
 "15017": "Poor Negro",
 "15019": "N word",
 "15020": "Colored allocated",
 "15021": "Coloreds plural",
 "15022": "Colored included code",
 "15023": "Colored community",
 "15024": "Colored neighborhood",
 "15025": "Colored business",
 "15026": "Colored politics",
 "15028": "Colored ambiguous,check next",
 "15029": "Colored ambiguous,check text",
 "15030": "Black, allocated",
 "15031": "Blacks, plural",
 "15032": "Black, included code",
 "15033": "Black culture",
 "15034": "Black neighborhood",
 "15035": "Black business",
 "15036": "Black politics",
 "15038": "Black ambiguous,check next",
 "15039": "Black ambiguous,check text",
 "15040": "African American",
 "15041": "African Americans, plural",
 "15043": "African American community",
 "15044": "African American neighborhood",
 "15045": "African American business",
 "15046": "African American politics",
 "15050": "People of color, allocated",
 "15052": "of color, included code",
 "15053": "Community of color",
 "15054": "Neighborhood of color",
 "15055": "Business of color",
 "15059": "of color, check text",
 "15060": "Black and Brown, allocated",
 "15061": "Blacks and Browns, plural",
 "15062": "Black and Brown, coded",
 "15063": "Black and Brown community",
 "15064": "Black and Brown neighborhood",
 "15065": "Black and Brown business",
 "15067": "Blacks and Latinos",
 "15068": "Black and Brown ambig chk next tokens",
 "15069": "Black and Brown ambig chk text",
 "15070": "Nonwhite",
 "15071": "Nonwhites, plural",
 "15073": "Nonwhite community",
 "15074": "Nonwhite neighborhood",
 "15075": "Nonwhite business",
 "15078": "Nonwhite ambiguous,check next",
 "15079": "Nonwhite ambiguous,check text",

 "15090": "Black and White: allocated",
 "15091": "Blacks and Whites: plural",
 "15092": "Black and White: included code",
 "15093": "Black and White: community",
 "15094": "Black and White: neighborhood",
 "15095": "Black and White: business",
 "15098": "Black and White: check next",
 "15099": "Black and White: check text",

 "15110": "White, allocated",
 "15111": "Whites, plural",
 "15112": "White, included coded",
 "15113": "White community",
 "15114": "White neighborhood",
 "15115": "White business",
 "15116": "White politics",
 "15117": "White slur: whitey",
 "15118": "ambiguous white, check next",
 "15119": "ambiguous white, check text",

 "15130": "Latino",
 "15131": "Mexican-American",
 "15133": "Dominican American",
 "15134": "Cuban American",
 "15135": "Hispanic",
 "15136": "Latinx",
 "15137": "Spanish speaking",
 "15138": "ambiguous Latino, maybe race",
 "15139": "Latino political group",

 "15140": "Asian Americans",
 "15141": "Chinese Americans",
 "15142": "Japanese Americans",
 "15143": "Filipino Americans",
 "15144": "Vietnamese Americans",
 "15145": "Korean Americans",
 "15146": "South Asian Americans",
 "15147": "Arab/Muslim Americans",
 "15148": "Native Hawaiian & Pacific Islander",
 "15149": "Anti-Asian",

 "15150": "Named Native American Tribal",
 "15151": "Native Americans",
 "15153": "Native American political group",
 "15155": "Native American political protest",
 "15156": "Native American political leader",
 "15157": "Native American victim",
 "15158": "Indigenous, tribal",

 "15160": "Ethnic",
 "15163": "White Ethnic",

 "15170": "immigrants",
 "15171": "immigrate",
 "15172": "immigration",
 "15173": "refugee",
 "15174": "citizenship",
 "15175": "foreigner",
 "15176": "First generation (ambig)",
 "15177": "Migrant (ambig)",
 "15178": "Pro-immigrant group",
 "15180": "illegal aliens",
 "15181": "Xenophobe",
 "15182": "other Anti-immigrant prejudice",
 "15184": "deport",
 "15186": "Anti-immigrant group",
 "15188": "Alien",

 "15191": "African immigrant",
 "15192": "Haitian immigrant",
 "15193": "Jamaican immigrant",
 "15198": "Afro Caribbean",
*/

gen int blackyes=0
	replace blackyes= mentions if occ2010>=15030 & occ2010<=15036	/* excludes ambiguous black 15038-9 */
	replace blackyes= mentions if occ2010>=15090 & occ2010<=15096	/* black and white, included */
	replace blackyes= mentions if occ2010>=15060 & occ2010<=15066	/* black and brown, included */
	replace blackyes= mentions if occ2010==15067                 	/* blacks and latinos */
	* middle class and poor blacks includes also middle class and poor [minorities, African Americans, etc.}
	replace blackyes= mentions if occ2010==10022                 	/* middle class blacks */
	replace blackyes= mentions if occ2010==15037                 	/* poor blacks */
	replace blackyes= mentions if occ2010==10464                 	/* HBCU */
	replace blackyes= mentions if occ2010==15019 					/*  n-word */
	label variable blackyes "15030-6 Black (included)"
	summarize blackyes if blackyes>=1, detail
	tab  occ2010 if blackyes>=1 & blackyes<., sort

gen int blackambig=0
	replace blackambig= mentions if occ2010==15038 /* ambiguous black 15038 */
	replace blackambig= mentions if occ2010==15039 /* ambiguous black 15039 */
	replace blackambig= mentions if occ2010==15068 /* ambiguous black and brown 15068 */
	replace blackambig= mentions if occ2010==15098 /* ambiguous black and white 15098 */
	label variable blackambig "15038,68,78 ambiguous Black"
	summarize blackambig if blackambig>=1, detail
	tab  occ2010 if blackambig>=1 & blackambig<., sort

gen int blackno=0
	replace blackno= mentions if occ2010==31910 /* black, excluded 31910 */
	replace blackno= mentions if occ2010==28276 /* Justice Hugo black 30076 */
	replace blackno= mentions if occ2010==28476 /* Hugo black 30276 */
	replace blackno= mentions if occ2010==31912 /* black and white excluded */
	replace blackno= mentions if occ2010==30011 /* b&w television */
	replace blackno= mentions if occ2010==31913 /* black and brown excluded */
	label variable blackno "31910,2 black, excluded"
	summarize blackno if blackno>=1, detail
	tab occ2010 if blackno>=1 & blackno<., sort

egen int blackany= rowtotal(blackambig blackyes blackno)
	label variable blackany "15200-67,38 blackyes+ blackambig+ blackno+ blackchess"
	summarize blackany if blackany>=1, detail
	tab occ2010 if blackany>=1 & blackany<., sort

gen int Nword=0
	replace Nword= mentions if occ2010==15019 					/*  n-word */
	label variable Nword "15019 N-word"
	summarize Nword if Nword>=1, detail
	tab  occ2010 if Nword>=1 & Nword<., sort

/*
gen int blackyesPlur=0
	replace blackyesPlur= mentions if occ2010==15031 /* only 15031 */
	order blackyesPlur, after(blackyes)
	label variable blackyesPlur "15031 Blacks (included&plurals)"
	summarize blackyesPlur if blackyesPlur>=1, detail
	tab  occ2010 if blackyesPlur>=1 & blackyesPlur<., sort
*/

******************  Negro  **********************************
* Negro is never ambiguous
gen int negro=0
	replace negro= mentions if occ2010>=15010 & occ2010<=15016	
	label variable negro "15010-6 Negroes"
	summarize negro if negro>=1, detail
	tab  occ2010 if negro>=1 & negro<., sort

******************  colored  **********************************
gen int coloredyes=0
	replace coloredyes= mentions if occ2010>=15020 & occ2010<=15027
	label variable coloredyes "15020-6 Coloreds (included)"
	summarize coloredyes if coloredyes>=1, detail
	tab  occ2010 if coloredyes>=1 & coloredyes<., sort

gen int coloredambig=0
	replace coloredambig= mentions if occ2010==15028
	replace coloredambig= mentions if occ2010==15029
	label variable coloredambig "15098,9 colored ambiguous"
	summarize coloredambig if coloredambig>=1, detail
	tab  occ2010 if coloredambig>=1 & coloredambig<., sort

gen int coloredno=0
	replace coloredno= mentions if occ2010==31914 /* colored excluded */
	label variable coloredno "31914 colored, excluded"
	summarize coloredno if coloredno>=1, detail
	tab  occ2010 if coloredno>=1 & coloredno<., sort

egen int coloredany= rowtotal(coloredyes coloredambig coloredno)
	label variable coloredany "15020-9,31914 colored, excluded"
	summarize coloredany if coloredany>=1, detail
	tab  occ2010 if coloredany>=1 & coloredany<., sort


******************  African American  **********************************
* African American is never ambiguous
gen int afamericans=0
	replace afamericans= mentions if occ2010>=15040 & occ2010<=15047
	label variable afamericans "15040-6 African Americans"
	summarize afamericans if afamericans>=1, detail
	tab  occ2010 if afamericans>=1 & afamericans<., sort

******************  [people] of color  **********************************
* for now, allocating ambiguous "of color" based on the *prior* word, not yet done in jobs.py
*	so, more hits remain in the ofcolorambig category
gen int ofcoloryes=0
	replace ofcoloryes= mentions if occ2010>=15050 & occ2010<=15057
	label variable ofcoloryes "15050-6 People of color"
	summarize ofcoloryes if ofcoloryes>=1, detail
	tab  occ2010 if ofcoloryes>=1 & ofcoloryes<., sort

gen int ofcolorambig=0
	replace ofcolorambig= mentions if occ2010==15058
	replace ofcolorambig= mentions if occ2010==15059  /* should be empty */
	label variable ofcolorambig "15058 ofcolor ambiguous"
	summarize ofcolorambig if ofcolorambig>=1, detail
	* should be only 15058 (after 6 April 2023)
	tab  occ2010 if ofcolorambig>=1 & ofcolorambig<., sort

gen int ofcolorno=0
	replace ofcolorno= mentions if occ2010==31916 /* of color excluded */
	label variable ofcolorno "31916 of color, excluded"
	summarize ofcolorno if ofcolorno>=1, detail
	tab  occ2010 if ofcolorno>=1 & ofcolorno<., sort

egen int ofcolorany= rowtotal(ofcoloryes ofcolorno ofcolorambig)
	label variable ofcolorany "15050-9,31916 of color"
	summarize ofcolorany if ofcolorany>=1, detail
	tab  occ2010 if ofcolorany>=1 & ofcolorany<., sort

******************  black and brown  **********************************
* black and brown is already included in blackany
gen int blackbrown=0
	replace blackbrown= mentions if occ2010>=15060 & occ2010<=15067
	label variable blackbrown "15060-6 Black & Brown"
	summarize blackbrown if blackbrown>=1, detail
	tab  occ2010 if blackbrown>=1 & blackbrown<., sort

gen int bbambig=0
	replace bbambig= mentions if occ2010==15068
	replace bbambig= mentions if occ2010==15069
	label variable bbambig "15068,9 black|brown ambiguous"
	summarize bbambig if bbambig>=1, detail
	tab  occ2010 if bbambig>=1 & bbambig<., sort

gen int bbno=0
	replace bbno= mentions if occ2010==31913 /* black and brown excluded */
	label variable bbno"31912 Black & Brown, excluded"
	summarize bbno if bbno>=1, detail
	tab  occ2010 if bbno>=1 & bbno<., sort

egen int bbany= rowtotal(blackbrown bbambig bbno)
	label variable bbany "1509?,31912 Black & Brown, any"
	summarize bbany if bbany>=1, detail
	tab  occ2010 if bbany>=1 & bbany<., sort

******************  black and white  **********************************
gen int blackwhite=0
	#replace blackwhite= mentions if occ2010>=15090 & occ2010<=15097
	replace blackwhite= mentions if occ2010==15090
	replace blackwhite= mentions if occ2010==15091
	replace blackwhite= mentions if occ2010==15092
	replace blackwhite= mentions if occ2010==15093
	replace blackwhite= mentions if occ2010==15094
	replace blackwhite= mentions if occ2010==15095
	replace blackwhite= mentions if occ2010==15096
	replace blackwhite= mentions if occ2010==15097
	label variable blackwhite "15090-6 Black & White"
	summarize blackwhite if blackwhite>=1, detail
	tab  occ2010 if blackwhite>=1 & blackwhite<., sort

gen int bwambig=0
	replace bwambig= mentions if occ2010==15098
	replace bwambig= mentions if occ2010==15099
	label variable bwambig "15098,9 Black & White ambiguous"
	summarize bwambig if bwambig>=1, detail
	tab  occ2010 if bwambig>=1 & bwambig<., sort

gen int bwno=0
	replace bwno= mentions if occ2010==30011 /* b&w television */
	replace bwno= mentions if occ2010==31912 /* black and white excluded */
	label variable bwno "31912 Black & White, excluded"
	summarize bwno if bwno>=1, detail
	tab  occ2010 if bwno>=1 & bwno<., sort

egen int bwany= rowtotal(blackwhite bwambig bwno)
	label variable bwany "1509?,31912 Black & White, any"
	summarize bwany if bwany>=1, detail
	tab  occ2010 if bwany>=1 & bwany<., sort

******************  minority **********************************
gen int minorityyes=0
	replace minorityyes= mentions if occ2010>=15000 & occ2010<=15007	
	label variable minorityyes "15000-6 Minorities"
	summarize minority if minorityyes>=1, detail
	tab  occ2010 if minorityyes>=1 & minorityyes<., sort

gen int minorityambig=0
	replace minorityambig= mentions if occ2010==15008
	replace minorityambig= mentions if occ2010==15009
	label variable minorityambig "15008,0 minority"
	summarize minorityambig if minorityambig>=1, detail
	tab  occ2010 if minorityambig>=1 & minorityambig<., sort

gen int minorityno=0
	replace minorityno= mentions if occ2010==31915 /* minbority excluded */
	label variable minorityno "31915 minority, excluded"
	summarize minorityno if minorityno>=1, detail
	tab  occ2010 if minorityno>=1 & minorityno<., sort

egen int minorityany= rowtotal(minorityyes minorityambig minorityno)
	label variable minorityany "15000-9,31915 minority"
	summarize minorityany if minorityany>=1, detail
	tab  occ2010 if minorityany>=1 & minorityany<., sort

******************  nonwhite **********************************
* nonwhite is never ambiguous
gen int nonwhite=0
	replace nonwhite= mentions if occ2010>=15070 & occ2010<=15077
	label variable nonwhite "15070-7 Nonwhites"
	summarize nonwhite if nonwhite>=1, detail
	tab  occ2010 if nonwhite>=1 & nonwhite<., sort

******************  Black immigrants **********************************
gen int blackimmig=0
	replace blackimmig= mentions if occ2010==15191 /* African immigrant */
	replace blackimmig= mentions if occ2010==15192 /* Haitian immigrant */
	replace blackimmig= mentions if occ2010==15193 /* Jamaican immigrant */
	replace blackimmig= mentions if occ2010==15198 /* Afro-Caribbean */
	label variable blackimmig "15091-3 Black immigrant"
	summarize blackimmig if blackimmig>=1, detail
	tab  occ2010 if blackimmig>=1 & blackimmig<., sort

******************  bplus **********************************
* bplusany is any word/phrase that may signify Blacks:
egen int bplusany= rowtotal(blackany negro coloredany afamericans ofcolorany minorityany nonwhite blackimmig )
	*replace bplusany= mentions if occ2010==9772	/* dropped: black etc. employee */
	replace bplusany= mentions if occ2010==10022	/* black etc. middle class */
	replace bplusany= mentions if occ2010==15037	/* poor blacks etc. */
	*replace bplusany= mentions if occ2010==10382	/* dropped: black etc.citizen */
	*replace bplusany= mentions if occ2010==10385	/* dropped: black etc.resident */
	*replace bplusany= mentions if occ2010==10389	/* dropped: black etc.voter */
	replace bplusany= mentions if occ2010==10464	/* HBCU*/
	replace bplusany= mentions if occ2010==15019   /* N word */
	*replace bplusany= mentions if occ2010==15122   /* dsicrimination against blacks */
	*order bplusany, after(blackyes)
	label variable bplusany "15000-15067 blackany,negro,etc + black workers"
	summarize bplusany if bplusany>=1, detail
	tab  occ2010 if bplusany>=1 & bplusany<., sort

/*
gen int bplusanyPlur=0
	replace bplusanyPlur= plurals if bplusany>0
	label variable bplusanyPlur "15000-15047 Black,plus. plurals"
	*order bplusanyPlur, after(bplusany)
	summarize bplusanyPlur if bplusanyPlur>=1, detail
	tab  occ2010 if bplusanyPlur>=1 & bplusanyPlur<., sort

gen int bplusanySing=0
	replace bplusanySing= mentions-plurals if occ2010>=15120 & occ2010<=15129 /* includes ambiguous black 15128 */
	replace bplusanySing= mentions-plurals if occ2010==10042	/* poor blacks */
	replace bplusanySing= mentions-plurals if occ2010==9772	/* working blacks */
	*label variable bplusanySing "15120-8 Black, singular"
	summarize bplusanySing if bplusanySing>=1, detail
*/

* bplusyes is a word/phrase that definitely signifies Blacks:
egen int bplusyes= rowtotal(blackyes negro coloredyes afamericans ofcoloryes minorityyes nonwhite blackimmig )
	replace bplusyes= mentions if occ2010==10022	/* black etc. middle class */
	replace bplusyes= mentions if occ2010==15037	/* poor blacks etc. */
	replace bplusyes= mentions if occ2010==10464	/* HBCU*/
	replace bplusyes= mentions if occ2010==15019   /* N word */
	label variable bplusyes "15000-15067 blackyes,negro,etc + black workers"
	summarize bplusyes if bplusyes>=1, detail
	tab  occ2010 if bplusyes>=1 & bplusyes<., sort

* bplusno is a word/phrase that definitely does not signify Blacks:
egen int bplusno= rowtotal(blackno coloredno ofcolorno minorityno )
	label variable bplusno "15000-15067 blackno,minorityno,etc"
	summarize bplusno if bplusno>=1, detail
	tab  occ2010 if bplusno>=1 & bplusno<., sort

* bplusambig is a word/phrase that may or may not signify Blacks:
egen int bplusambig= rowtotal(blackambig coloredambig ofcolorambig minorityambig )
	label variable bplusambig "15000-15067 blackambig,coloredambig,etc"
	summarize bplusambig if bplusambig>=1, detail
	tab  occ2010 if bplusambig>=1 & bplusambig<., sort

*********************** Other label for Blacks other than black  *************************************
egen int botherany= rowtotal(negro coloredany afamericans ofcolorany minorityany nonwhite)
	replace botherany= mentions if occ2010==15019   /* N word */
	replace botherany= mentions if occ2010==15403   /* black Muslims */
	label variable botherany "15000+ African Americans,minority,etc not black"
	summarize botherany if botherany>=1, detail
	tab  occ2010 if botherany>=1 & botherany<., sort

/*********************** Whites *************************************
 "15110": "White",
 "15111": "Whites",
 "15113": "White community",
 "15114": "White neighborhood",
 "15115": "White business",
 "15116": "White politics",
 "15118": "ambiguous white, check next tokens",
 "15119": "ambiguous white, check text context",
*/
gen int whiteyes=0
	replace whiteyes= mentions if occ2010>=15110 & occ2010<=15116	/* excludes ambiguous white 15118-9 */
	replace whiteyes= mentions if occ2010>=15090 & occ2010<=15096	/* black and white, included */
	replace whiteyes= mentions if occ2010==15117	/* poor whites */
	*replace whiteyes= mentions if occ2010==9771	/* working whites */
	*replace whiteyes= mentions if occ2010==10384	/* white resident */
	*replace whiteyes= mentions if occ2010==10388	/* white voter */
	replace whiteyes= mentions if occ2010==11384	/* discrimination against whites */
	replace whiteyes= mentions if occ2010==15223 /* white power 15223 */
	label variable whiteyes "15110-6 whites"
	summarize whiteyes if whiteyes>=1, detail
	tab  occ2010 if whiteyes>=1 & whiteyes<., sort

gen int whiteambig=0
	replace whiteambig= mentions if occ2010==15118 /* ambiguous white 15118 */
	replace whiteambig= mentions if occ2010==15119 /* ambiguous White 15119 */
	replace whiteambig= mentions if occ2010==15099 /* ambiguous Black and White 15099 */
	label variable whiteambig "15117-9 ambiguous White"
	summarize whiteambig if whiteambig>=1, detail
	tab  occ2010 if whiteambig>=1 & whiteambig<., sort

/*
gen int whitesPlur=0
	replace whitesPlur= plurals if whites>0
	label variable whitesPlur "15110-6 Whites, plurals"
	summarize whitesPlur if whitesPlur>=1 & whitesPlur<., detail
	tab  occ2010 if whitesPlur>=1 & whitesPlur<., sort
*/

gen int whiteno=0
	replace whiteno= mentions if occ2010==31911 /* white, excluded 31911 */
	replace whiteno= mentions if occ2010==31912 /* black and white, excluded 31912 */
	replace whiteno= mentions if occ2010==14020 /* white house 104020 */
	replace whiteno= mentions if occ2010==10029 /* white collar 10029 */
	replace whiteno= mentions if occ2010==10920 /* white collar criminal 10920 */
	replace whiteno= mentions if occ2010==10990 /* white collar crime 10980 */
	replace whiteno= mentions if occ2010==30293 /* Byron White 30293 */
	replace whiteno= mentions if occ2010==30093 /* Justice Byron White 30093 */
	label variable whiteno "31911 white, excluded"
	summarize whiteno if whiteno>=1, detail
	tab  occ2010 if whiteno>=1 & whiteno<., sort

egen int whiteany= rowtotal(whiteyes whiteambig whiteno)
	label variable whiteany "15110-7,38 whites+ whiteambig+ whiteno+ whitechess"
	summarize whiteany if whiteany>=1, detail
	tab  occ2010 if whiteany>=1 & whiteany<., sort

/*********************** Latinx, Hispanic [later, needs own program] *************************************
gen int latino0=0
	replace latino= mentions if occ2010==15130
	label variable latino0 "15130 Latino, Latina"
	summarize latino0 if latino0>=1, detail

gen int mexicanam=0
	replace mexicanam= mentions if occ2010==15131
	label variable mexicanam "15131 Mexican American"
	summarize mexicanam if mexicanam>=1, detail

* puerto rican code 18630 includes anything about Puerto Rico, in continental US or Puerto Rico itself
gen int puertorican=0
	replace puertorican= mentions if occ2010==18630
	replace puertorican= mentions if occ2010==15132	/* obsolete, before 10/2022 was part of latino code */
	label variable puertorican "18630 Puerto Rican"
	summarize puertorican if puertorican>=1, detail

gen int dominican=0
	replace dominican= mentions if occ2010==15133
	label variable dominican "15133 Dominican American"
	summarize dominican if dominican>=1, detail

gen int cubanam=0
	replace cubanam= mentions if occ2010==15134
	label variable cubanam "15134 Cuban American"
	summarize cubanam if cubanam>=1, detail

gen int hispanic=0
	replace hispanic= mentions if occ2010==15135
	label variable hispanic "15135 Hispanic"
	summarize hispanic if hispanic>=1, detail

gen int latinx=0
	replace latinx= mentions if occ2010==15136
	label variable latinx "15136 Latinx (specifically)"
	summarize latinx if latinx>=1, detail

egen int latinplus= rowtotal (latino0 mexicanam puertorican dominican cubanam hispanic latinx)
	replace latinplus= mentions if occ2010==10043	/* poor Latino */
	replace latinplus= mentions if occ2010==15133   /* Dominican immigrants, Afro-Caribbean */
	label variable latinplus "15130-7 Latino, Hispanic, etc.+ Lworkers"
	summarize latinplus if latinplus>=1, detail
	tab occ2010 if latinplus>=1 & latinplus<., sort

gen int latinPlur= 0
    replace latinPlur= plurals if occ2010>=15130 & occ2010<=15139
	replace latinPlur= plurals if occ2010==10043	/* poor Latinx */
	label variable latinPlur "15130-9 Hispanics,Latinos, etc.plurals"
	summarize latinPlur if latinPlur>=1, detail
	tab occ2010 if latinPlur>=1 & latinPlur<., sort
*/




/*********************** Asian Americans [later, needs own program] *************************************
 "15140": "Asian Americans",
 "15141": "Chinese Americans",
 "15142": "Japanese Americans",
 "15143": "Filipino Americans",
 "15144": "Vietnamese Americans",
 "15145": "Korean Americans",
 "15146": "South Asian Americans",
 "15147": "Arab/Muslim Americans",
 "15148": "Native Hawaiian & Pacific Islander",
*/
/*
gen int asianam0= 0
replace asianam0= mentions if occ2010==15140
	label variable asianam0 "15140 Asian Americans (specifically)"
	summarize asianam0 if asianam0>=1, detail

gen int chineseam= 0
replace chineseam= mentions if occ2010==15141
	label variable chineseam "15141 Chinese Americans"
	summarize chineseam if chineseam>=1, detail

gen int japaneseam= 0
replace japaneseam= mentions if occ2010==15142
	label variable japaneseam "15142 Japanese Americans"
	summarize japaneseam if japaneseam>=1, detail

gen int filipinoam= 0
replace filipinoam= mentions if occ2010==15143
	label variable filipinoam "15143 Filipino Americans"
	summarize filipinoam if filipinoam>=1, detail

gen int vietnameseam= 0
replace vietnameseam= mentions if occ2010==15144
	label variable vietnameseam "15144 Vietnamese Americans"
	summarize vietnameseam if vietnameseam>=1, detail

gen int koreanam= 0
replace koreanam= mentions if occ2010==15145
	label variable koreanam "15145 Korean Americans"
	summarize koreanam if koreanam>=1, detail

gen int southasianam= 0
replace southasianam= mentions if occ2010==15146
	label variable southasianam "15146 South Asian Americans"
	summarize southasianam if southasianam>=1, detail

gen int arabam= 0
replace arabam= mentions if occ2010==15147
	label variable arabam "15147 Arab, Muslim Americans"
	summarize arabam if arabam>=1, detail

gen int hawaiian= 0
replace hawaiian= mentions if occ2010==15148
	label variable hawaiian "15148 Hawaiian + Pacific islander"
	summarize hawaiian if hawaiian>=1, detail

egen int asianam= rowtotal (asianam0 chineseam japaneseam filipinoam vietnameseam koreanam southasianam arabam hawaiian)
	label variable asianam "15140-8 Asian Americans + Hawaiian"
	summarize asianam if asianam>=1, detail
	tab occ2010 if asianam>=1 & asianam<., sort

gen int asianamPlur= 0
replace asianamPlur= plurals if asianam>0
	label variable asianamPlur "15140-8 Asian American, plurals"
	summarize asianamPlur if asianamPlur>=1, detail
	tab occ2010 if asianamPlur>=1 & asianamPlur<., sort
*/

******************** collapse to document level ***********************
sort article mentions occ2010
collapse (sum) mentions plurals documents blackyes-pcorruption (last) occ2010 , by(article)


* now disambiguate bias, black, etc. based on racial content of whole document

*********************** bias(general) AND race = biasB  ************************
* first get better measures of bias that include disambiguated bias
* 	 fix summary racialbias to include biasrace:
gen int biasB=0
	replace  biasB= bias6 if race5>=1 & race5<.
	*  was bplusany>=1
	replace  biasB= bias6 if bplusyes>=1 & bplusyes<.
	replace  biasB= bias6 if bplusambig>=1 & bplusambig<.
	label variable  biasB "11201-4 bias6 @ (race U bplusyes) doc"
	order  biasB, after(bias6)
	summarize biasB if biasB>=1, detail
	summarize bias6 if bias6>=1, detail

* now include the updated  biasB in the racial5B scale:
*egen int racial4= rowtotal (rprejudice rdiscrim racial racialineq)
egen int racial5B= rowtotal(rprejudice rdiscrim racial racialineq  biasB)
	label variable racial5B "15220-15289 racial bias w  biasB"
	summarize racial5B if racial5B>=1, detail
	summarize racism6   if racism6  >=1, detail
	order racial5B, after(racial4)

* create (final) overall racial issues measure:
*egen int race4=rowtotal(racialeq4 antiracism3 racism6 racial4)
egen int race4B= rowtotal(racialeq4 antiracism3 racism6 racial5B)
	label variable race4B "15270-98,11201-4 4 race scales+ biasB"
	summarize race4B if race4B>=1, detail
	order race4B, after(race4)

egen int race5B= rowtotal(racialeq4 antiracism3 racism6 racial5B apartheid)
	label variable race5B "15270-98,11201-4 race5B + apartheid"
	summarize race5B if race5B>=1, detail
	order race5B, after(race4B)

*********************** blackambig AND race,black  = black ************************
* disambiguate blackambig based on whether whole document has some racial referent (race4) or not
* first drop blackyes for chess document
gen byte blackchess=0
	replace blackchess= blackambig if chess>=1
	replace blackambig= 0          if chess>=1
	replace blackchess= blackany   if chess>=1
	replace blackyes=0              if chess>=1
	label variable blackchess "15230,8 black in chess doc"
	summarize blackchess if blackchess>=1, detail
	order blackchess, after(blackno)

* then disambiguate black when not an included or excluded black phrase:
*	if a racial theme somewhere in the document, then black is racial
gen byte blackarace=0
	replace blackarace= blackambig if blackambig>=1 & race5>=1
	replace blackarace= blackambig if blackambig>=1 & blackyes>=1
	label variable blackarace "15238 blackambig+ race,blacks doc"
	summarize blackarace if blackarace>=1, detail
	order blackarace, after(blackambig)

gen byte blackano=0
	replace blackano= blackambig if blackambig>=1 & race5==0
	label variable blackano "15238 blackambig+ no race,blacks doc"
	summarize blackano if blackano>=1, detail
	order blackano, after(blackarace)

* blackrace is a final count of black that is coded as racial
*	it does not depend on any race subscales that depend on a black theme in the text (e.g., race5B)
*	so the correlation with race4 is not an artifact of race4 incorporating black
*		but, of course, blackarace does incorporate race4
egen byte blackrace= rowtotal(blackarace blackyes)
	label variable blackrace "15200-67,38 blackambig + race or blacks doc"
	summarize blackrace if blackrace>=1, detail
	order blackrace, after(blackany)

* blacknone is the final count of black that is not coded as racial
egen byte blacknone= rowtotal (blackno blackchess blackano)
*	occasionally an doc may have both; but blacknone is for no racial meaning anywhere in doc
	replace blacknone=0 if blackrace>0
	label variable blacknone "31910 black but no black race"
	summarize blacknone if blacknone>=1, detail
	order blacknone, after(blackrace)

*********************** whiteambig AND race5,white  = white ************************
* first drop whiteyes code for chess docs:
gen byte whitechess=0
	replace whitechess= whiteambig if chess>=1
	replace whiteambig= 0          if chess>=1
	replace whitechess= whiteyes  if chess>=1
	replace whiteyes=0            if chess>=1
	label variable whitechess "15110,8 white chess"
	summarize whitechess if whitechess>=1, detail
	order whitechess, before(whiteno)

* then disambiguate white when not an included or excluded phrase
gen byte whitearace=0
	replace whitearace= whiteambig if whiteambig>=1 & race5>=1
	replace whitearace= whiteambig if whiteambig>=1 & whiteyes>=1
	label variable whitearace "15238 whiteambig+ race,whites doc"
	summarize whitearace if whitearace>=1, detail
	order whitearace, after(whiteambig)

gen byte whiteano=0
	replace whiteano= whiteambig if whiteambig>=1 & race5==0 & whiteyes==0
	label variable whiteano "15238 whiteambig+ no race,whites doc"
	summarize whiteano if whiteano>=1, detail
	order whiteano, after(whitearace)

* whiterace is a final count of white that is coded as racial
egen byte whiterace= rowtotal(whitearace whiteyes)
	label variable whiterace "15200-67,38 whiteyes + whiteambig/race doc"
	summarize whiterace if whiterace>=1, detail
	order whiterace, after(whiteno)

egen byte whitenone= rowtotal (whiteno whitechess whiteano)
*	occasionally an document may have both; but whitenone is for no racial meaning anywhere in document
	replace whitenone=0 if whiterace>0
	label variable whitenone "31910 white but no white race"
	summarize whitenone if whitenone>=1, detail
	order whitenone, after(whiterace)

*********************** minorityambig AND race4 = minorityarace ************************
gen byte minorityarace=0
	replace minorityarace= minorityambig if minorityambig>=1 & race5>=1
	label variable minorityarace "15008 minorityambig+ race doc"
	summarize minorityarace if minorityarace>=1, detail
	order minorityarace, after(minorityambig)

gen byte minorityano=0
	replace minorityano= minorityambig if minorityambig>=1 & race5==0
	label variable minorityano "15008 minorityambig+ no race doc"
	summarize minorityano if minorityano>=1, detail
	order minorityano, after(minorityarace)

egen byte minorityrace= rowtotal(minorityarace minorityyes)
	label variable minorityrace "15000-8 minorityyes|minorityambig + race doc"
	summarize minorityrace if minorityrace>=1, detail
	order minorityrace, after(minorityarace)

egen byte minoritynone= rowtotal (minorityno minorityano)
	replace minoritynone=0 if minorityrace>0
	label variable minoritynone "31915 minority but no race"
	summarize minoritynone if minoritynone>=1, detail
	order minoritynone, after(minorityno)

*********************** coloredambig AND race = colored ************************
gen byte coloredarace=0
	replace coloredarace= coloredambig if coloredambig>=1 & race5>=1
	label variable coloredarace "15028 coloredambig+ race doc"
	summarize coloredarace if coloredarace>=1, detail
	order coloredarace, after(coloredambig)

gen byte coloredano=0
	replace coloredano= coloredambig if coloredambig>=1 & race5==0
	label variable coloredano "15028 coloredambig+ no race doc"
	summarize coloredano if coloredano>=1, detail
	order coloredano, after(coloredarace)

egen byte coloredrace= rowtotal(coloredarace coloredyes)
	label variable coloredrace "15020-8 coloredyes|coloredambig + race doc"
	summarize coloredrace if coloredrace>=1, detail
	order coloredrace, after(coloredarace)

egen byte colorednone= rowtotal (coloredno coloredano)
	replace colorednone=0 if coloredrace>0
	label variable colorednone "31914+ colored but no race"
	summarize colorednone if colorednone>=1, detail
	order colorednone, after(coloredno)

*********************** ofcolorambig AND race = ofcolor ************************
gen byte ofcolorarace=0
	replace ofcolorarace= ofcolorambig if ofcolorambig>=1 & race5>=1
	label variable ofcolorarace "15008 ofcolorambig+ race doc"
	summarize ofcolorarace if ofcolorarace>=1, detail
	order ofcolorarace, after(ofcolorambig)

gen byte ofcolorano=0
	replace ofcolorano= ofcolorambig if ofcolorambig>=1 & race5==0
	label variable ofcolorano "15008 ofcolorambig+ no race doc"
	summarize ofcolorano if ofcolorano>=1, detail
	order ofcolorano, after(ofcolorarace)

egen byte ofcolorrace= rowtotal(ofcolorarace ofcoloryes)
	label variable ofcolorrace "15000-8 ofcoloryes|ofcolorarace"
	summarize ofcolorrace if ofcolorrace>=1, detail
	order ofcolorrace, after(ofcolorarace)

egen byte ofcolornone= rowtotal (ofcolorno ofcolorano)
	replace ofcolornone=0 if ofcolorrace>0
	label variable ofcolornone "31916+ ofcolor but no race"
	summarize ofcolornone if ofcolornone>=1, detail
	order ofcolornone, after(ofcolorno)

*********************** overall black mentions, whether black, African American, etc. ************************
* also includes black,etc. ambiguous recoded as racial based on race>0 in text
*	should disambiguate blackwhite, blackbrown as well but not needed for bplus because already in black vars
*		ie. blackyes includes bbyes; blackambig includes bbambig, blackno includes bbno

* bplusrace is the best overall measure of inclusion of Blacks in a document
egen int bplusrace= rowtotal(blackrace negro afamericans coloredrace ofcolorrace minorityrace nonwhite)
	order bplusrace, after(bplusany)
	label variable bplusrace "15000-15067 Blacks,Negroes,etc disambiguated"
	summarize bplusrace if bplusrace>=1, detail

egen int bplusarace= rowtotal(blackarace coloredarace ofcolorarace minorityarace )
	order bplusarace, after(bplusambig)
	label variable bplusarace "15008 black,minority,etc disambiguated=racial"
	summarize bplusarace if bplusarace>=1, detail

egen int bplusano= rowtotal(blackano coloredano ofcolorano minorityano )
	order bplusano, after(bplusarace)
	label variable bplusano "15008 black,minority,etc disambiguated=not racial"
	summarize bplusano if bplusano>=1, detail

gen int bplusnone= 0
	replace  bplusnone= bplusany if bplusrace==0
	order bplusnone, after(bplusrace)
	label variable bplusnone "15000-15067 no disambig Blacks,Negroes,etc in doc"
	summarize bplusnone if bplusnone>=1, detail

egen int botherrace= rowtotal(negro afamericans coloredrace ofcolorrace minorityrace nonwhite)
	order botherrace, after(botherany)
	label variable botherrace "15000-15067 African American,minority,etc.disambiguated"
	summarize botherrace if botherrace>=1, detail

gen int bothernone= 0
	replace  bothernone= botherany if botherrace==0
	order bothernone, after(botherrace)
	label variable bothernone "15000-15067 minority,colored,etc not black in doc"
	summarize bothernone if bothernone>=1, detail

gen int racebplus= race4
	replace racebplus= bplusrace if bplusrace>0
	order racebplus, after(race4)
	label variable racebplus "15000-67,15270-98,11201-4 blacks,etc.race,antiracism,bias(race)"
	summarize bothernone if bothernone>=1, detail

duplicates report article
sort article

foreach var of varlist blackyes-pcorruption {
	gen byte y`var'= 0
	replace y`var'= 1 if `var'>0 & `var'<.
	}

alpha yaffaction yantiracist ybias6 ycivilrights yrdiscrim yracialineq yklanplus ymilitant yeqpolitics ///
     yrprejudice yeqprinciple yraceprotest yracial yracism0 yracistevent yracistlaw yrvictim ywhitepower, item label

egen raceissues= rowtotal( yaffaction yantiracist        ycivilrights yrdiscrim yracialineq yklanplus ymilitant yeqpolitics ///
 yrprejudice yeqprinciple yraceprotest yracial yracism0 yracistevent yracistlaw yrvictim ywhitepower)
	label variable raceissues "Count of 17 racial issues"
	summarize raceissues, detail
	order raceissues, after(race4)
	correl raceissues race4

	label variable yblackyes "15030-6 Black (included)"
	label variable yblackambig "15038,9 ambiguous Black"
	label variable yblackno "31910,2 black, excluded"
	label variable yblackany "15200-67,38 blackyes+ blackambig+ blackno+ blackchess"
	label variable yNword "15019 N-word"
	label variable ynegro "15010-6 Negroes"
	label variable ycoloredyes "15020-6 Coloreds (included)"
	label variable ycoloredambig "15098,9 colored ambiguous"
	label variable ycoloredno "31912 colored, excluded"
	label variable ycoloredany "15020-9,31912 colored, excluded"
	label variable yafamericans "15040-6 African Americans"
	label variable yofcoloryes "15050-6 People of color"
	label variable yofcolorambig "15058,9 ofcolor ambiguous"
	label variable yofcolorno "31916 of color, excluded"
	label variable yofcolorany "15050-9,31916 of color"
	label variable yblackbrown "15060-6 Black & Brown"
	label variable ybbambig "15068,9 black|brown ambiguous"
	label variable ybbno"31912 Black & Brown, excluded"
	label variable ybbany "1509?,31912 Black & Brown, any"
	label variable yblackwhite "15090-6 Black & White"
	label variable ybwambig "15098,9 Black & White ambiguous"
	label variable ybwno"31912 Black & White, excluded"
	label variable ybwany "1509?,31912 Black & White, any"
	label variable yminorityyes "15000-6 Minorities"
	label variable yminorityambig "15008,0 minority"
	label variable yminorityno "31915 minority, excluded"
	label variable yminorityany "15000-9,31915 minority"
	label variable ynonwhite "15070-6 Nonwhites"
	label variable yblackimmig "15090-6 Black immigrant"
	label variable ybplusany "15000-15067 black,negro,etc + black workers"
	label variable ybplusno "15000-15067 blacks,minority,etc not Blacks"
	label variable ybplusambig "15000-15067 black,minority,etc maybe Blacks"
	label variable ybotherany "15000+ African Americans,minority,etc not black"
	label variable ywhiteyes "15110-6 whites"
	label variable ywhiteambig "15117-9 ambiguous White"
	label variable ywhiteno "31911 white, excluded"
	label variable ywhiteany "15110-7,38 whites+ whiteambig+ whiteno+ whitechess"
	label variable yracial "15230-5 racial mention"
	label variable yracialineq "15230-5 racial inequality, segregation"
	label variable yapartheid "15244 apartheid"
	label variable yracialeq4 "15250-8 racial equality"
	label variable ycivilrights "15250,1 civil, voting rights"
	label variable yeqprinciple "15253 racial equality principle"
	label variable yaffaction "15253 affirmative action"
	label variable yeqpolitics "15257,8 antiracism law"
	label variable yantiracist "15261,2 81,9 antiracist group,leader"
	label variable ymilitant "15262 84,89 militant group,leader"
	label variable yraceprotest "15271-4 raceprotest movement"
	label variable yblacklm "15271 black lives matter"
	label variable yantiracism3 "15250-89 antiracism group policy"

	label variable yracism0 "15220 racism"
	label variable yrprejudice "15221 racial prejudice"
	label variable yrdiscrim "15222 racial discrimination"
	label variable ywhitepower "15223 white power"
	label variable yklan "15224,5 kkk, other racist group"
	label variable yracistlaw "15226 racist law, court"
	label variable yrvictim "15227 racist victim"
	label variable yracistevent "15229 racist event"
	label variable yracism6 "15220-9 racism codes"
	label variable yrace4 "15220-15289 all racial issues"
	label variable yrace5 "15220-15289 race4+apartheid"
	label variable ybias0 "15201 bias, not specififed"
	label variable yprejudice "15202 prejudice, not specififed"
	label variable yhate "15203 hate, not specififed"
	label variable yhatecrime "15204 hatecrime, not specififed"
	label variable yoprejudice "15206 other prejudices"
	label variable ydiscrimination "15211 discrimination, not specififed"
	label variable yoppression "15211 oppression, not specififed"
	label variable ybias6 "15201-12 prejudice discirmination, not specififed"
	label variable ychess "game of chess doc 10351"
	label variable ypolice "police mentions"
	label variable ypviolence "police violence & civ review boards, 17400-9"
	label variable ypcorruption "3855 police corruption"
	label variable ybiasB "11201-4 biasplus + race or blacks doc"
	label variable yracial5B "11201-4 biasplus + race or blacks doc"
	label variable yrace4B "15270-98,11201-4 race, antiracism, bias(race)"
	label variable yrace5B "15220-15289 race4B+apartheid"
	label variable yblackchess "15230,8 black in chess doc"
	label variable yblackarace "15238 blackambig+ race,blacks doc"
	label variable yblackano "15238 blackambig+ no race,blacks doc"
	label variable yblackrace "15200-67,38 blackambig + race or blacks doc"
	label variable yblacknone "31910 black but no black race"
	label variable ywhitechess "15110,8 white chess"
	label variable ywhitearace "15238 whiteambig+ race,whites doc"
	label variable ywhiteano "15238 whiteambig+ no race,whites doc"
	label variable ywhiterace "15200-67,38 whiteyes + whiteambig/race doc"
	label variable ywhitenone "31910 white but no white race"
	label variable yminorityarace "15008 minorityambig+ race doc"
	label variable yminorityano "15008 minorityambig+ no race doc"
	label variable yminorityrace "15000-8 minorityyes|minorityambig + race doc"
	label variable yminoritynone "31915 minority but no race"
	label variable ycoloredarace "15028 coloredambig+ race doc"
	label variable ycoloredano "15028 coloredambig+ no race doc"
	label variable ycoloredrace "15020-8 coloredyes|coloredambig + race doc"
	label variable ycolorednone "31914+ colored but no race"
	label variable yofcolorarace "15008 ofcolorambig+ race doc"
	label variable yofcolorano "15008 ofcolorambig+ no race doc"
	label variable yofcolorrace "15000-8 ofcoloryes|ofcolorambig + race doc"
	label variable yofcolornone "31916+ ofcolor but no race"
	label variable ybplusrace "15000-15067 Blacks,Negroes,etc disambiguated"
	label variable ybplusnone "15000-15067 no disambig Blacks,Negroes,etc in doc"
	label variable ybotherrace "15000-15067 African American,minority,etc.disambiguated"
	label variable ybothernone "15000-15067 minority,colored,etc not black in doc"
	label variable yracebplus "15000-67,15270-98,11201-4 blacks,etc.race,antiracism,bias(race)"

foreach var of varlist blackyes-pcorruption {
	gen byte y3`var'= 0
	replace y3`var'= 1 if `var'>2 & `var'<.
	}
	tab y3race4 y3blackyes, cell missing


summarize yblackyes-ypcorruption, sep(0)
summarize y3blackyes-y3pcorruption, sep(0)

/*
yblackany		
	blackracial	
		blackinclude
		blackarace
	blacknonracial	
		blackexclude
		blackambignot
AfricanAmerican		
Negro		
Nonwhite		
Minority		
	minorityracial	
	minoritynot	
Ofcolor		
	ofcolorracial	
	ofcolornot	
Colored		
	coloredracial	
	colorednot	
		
	BlackPlus	
		Other
*/

summarize yblackany yblackrace yblackyes yblackarace yblacknone yblackno yblackano ///
	yafamerican ynegro ynonwhite ///
	yminorityany yminorityyes yminorityrace yminoritynone ///
	yofcolorany yofcoloryes yofcolorrace yofcolornone ///
	ycoloredany ycoloredyes ycoloredrace ycolorednone ///
	ybplusany ybplusrace ybplusnone ybotherany ybotherrace ybothernone, sep(0)
	
/*
summarize y3blackany y3blackrace y3blackyes y3blackarace y3blacknone y3blackno y3blackano ///
	y3afamerican y3negro y3nonwhite ///
	y3minorityany y3minorityyes y3minorityrace y3minoritynone ///
	y3ofcolorany y3ofcoloryes y3ofcolorrace y3ofcolornone ///
	y3coloredany y3coloredyes y3coloredrace y3colorednone ///
	y3bplusany y3bplusrace y3bplusnone y3botherany y3botherrace y3bothernone, sep(0)
*/
	
summarize race4 race5B racialeq4 antiracism3 racism6 racial4 racial5B, sep(0)
summarize yrace4 yrace5B yracialeq4 yantiracism3 yracism6 yracial4 yracial5B, sep(0)
/*
race4=  rowtotal(racialeq4 antiracism3 racism6 racial4)
race5B= rowtotal(racialeq4 antiracism3 racism6 racial5B apartheid)

yracialeq4:
	yaffaction			
	yeqpolitics			
	ycivilrights			
	yeqprinciple			
antiracism3:
	antiracist
	militant
	raceprotest
racism6:
	yracism0
	yracistlaw
	yrvictim
	yklanplus
	yracistevent
	ywhitepower
racial4
	rprejudice
	rdiscrim
	racial
	racialineq
race4B=   rowtotal (racialeq4 antiracism3 racism6 racial5B)
racial5B= rowtotal (rprejudice rdiscrim racial racialineq  biasB)
biasB=    rowtotal (bias0 prejudice hatecrime oprejudice discrimination oppression) if race>0
bias6=    rowtotal (bias0 prejudice hatecrime oprejudice discrimination oppression)
	bias0
	prejudice
	hatecrime
	oprejudice
	discrimination
	oppression

summarize yaffaction yantiracist ybias6 ycivilrights yrdiscrim yracialineq yklanplus ymilitant yeqpolitics ///
 yrprejudice yeqprinciple yraceprotest yracial yracism0 yracistevent yracistlaw yrvictim ywhitepower, sep(0)
*/

summarize race4 race4B race5 race5B /// 
	yracialeq4 yaffaction   yeqpolitics   ycivilrights   yeqprinciple    ///
	antiracism3 antiracist militant raceprotest ///
	racism6 yracism0 yracistlaw yrvictim yklanplus yracistevent ywhitepower /// 
	bias6 biasB bias0 prejudice hatecrime oprejudice discrimination oppression ///
	apartheid

* end of racecounts.do:

