# ngrams.py
#	version 2.0.0
#		revision: jobs.* and occs.* renamed to ngrams. and codes.
#		revision: tries to disambiguate some words like black, poor, by checking whether following word is a code or not.
#		revision: adds disambiguation of capitalized/ non-capitalized titles (e.g., President, president)
#		titles to be disambiguated now have negative values in ngrams.json (e.g., "president": -12, )
#	reads a series of text files and identifies and codes all words, bigrams, trigrams, and ngrams in ngrams.json
#		juse to be ngrams.json
#		codes these ~40,000 "ngrams" into ~5000 codes including all 2010 3-digit U.S. Census occupation codes (10-9760)
#			some Census codes are subdivided: e.g., (CEOs: govt & pvt; 
#
#	arg= prefix is a filename prefix to output (& input) files
#		e.g. python3 ngrams.py NYT (will then look for list of documents to code in NYTfiles.txt)
#
#	input:
#		prefix+files.txt (e.g., NYTfiles.txt)= a file of filenames of text files to be read and coded.
#			this is the only input file created for each execution of ngrams.py
#			the other three files below are fixed inputs to ngrams.py
#		ngrams.json = a json file of ngrams with number codes (e.g., job titles with Census 2010 codes)
#			this file can always be improved and updated.
#			the ngrams.py program divides ngrams.json into four Python dicts: 1-word, 2-word, 3-word, and 4-word  ngram titles.
#			3-word phrase from text are checked first if it matches a 3-word titles (abc), 
#				then 2-word bigram are formed from those 3 words (ab, ac) and checked against ngrams.json, 
#				then the first word of the 3 is checked against one word titles from ngrams.json (a).
#				if no match, the program moves on to next 3-word phrase (bcd).
#				texts are checked only within a sentence (i.e., abc never spans two sentences)
#		codes.json = a json file of (the somewhat expanded) Census 2010 codes and their titles.
#		nosingularize.txt = a file of words (ngram titles) that should not be singularized in the texts
#			either they  would be incorrectly singularized by inflect.singnoun (e.g., boss, waitress)
#			or are in the plural in ngrams.json: bahamas, data, physics, royalties
#		plurals.txt = a file of words (ngram titles) included in nosingularize.txt that are actual plurals
#			or are in the plural in ngrams.json: bahamas, data, physics, royalties
#		two lists initialized below in the program, but probably would be more flexible as external files:
#			1 file of words that are coded as ngrams only if lower case (e.g., potter)
#			1 file of words that are coded as ngrams only if upper case (e.g., General)
#
#	to compile ngrams.py:
#		uses python standard packages: re json sys
#		uses python packages that must be downloaded and installed: nltk inflect BeautifulSoup
#
#	order of processing a text:
#		drop html
#		add end of paragraph marker (2 end of lines together) because the sentence tokenizer will ignore paragraphing:
#		drop newlines to make one long text:
#		replace hyphens with a space (except pre-k x-ray)
#		count words (spaces)
#		replace specified abbreviations (in abbrev.json) with replacement words
#			this avoids some mistaken sentece breaks
#			exceptions U.S.C. which is a legal code if preceded by a number (but might also be a Southern Cal sports score)
#		replace a single uppoercase letter abbreviation with just the letter (it's usually a middle initial)
#		replace multiple blanks with a single blank
#		make each line a complete sentence (using sent_tokenize)
#		change a fully uppercase line to a line with titles
#			or lower case?
#			need to fix input so Nexis article titles end with a period (ie are a sentence)
#		add EOL (a fake word) at the end of the sentence so that there is a final trigram for which the initial word can be coded
#			need to fix for 4-grams
#		replace commas with a space
#			enables long title with a comma to be handled correctly (University of California, Berkeley)
#		replace all other punctuation with surrounding blanks so the punctuation is treated as a separate word.
#		separate line into individual words (wordU)
#		for each wordU:
#			wordS= singularize the word unless it's in nosingularize.txt
#		create trigram, and bigrams for previous 1,2,3 words and a quadgram adding this new word to the previous 3
#			also creates a second bigram for 1 + 3, ignoring the word in between
#		checks for these ngrams in ngrams.json, starting with 4gram, then 3gram, then 2gram, then 2(1+3)gram, then word1
#			if code in ngrams.json is negative, then additional processing to adjust for upper/lower case meanings
#		
#
# todo (maybe):
#
#	separate person and nonperson codes so that disambiguating some words (e.g, black, poor, old) can distinguish social categories from nonsocial.
#	recheck that all "st xxx" are also "saint xxx" and vice-versa
#
#	for notTitle (e.g., General, ) don't treat as title if first word in sentence 
#		done: or in article title.
#	for notTitle (e.g., General, ) check when word is first encountered in line, not when proessing uni, bi, and trigrams
#
#	Japanese Diet: add wordbi2 to notLower
#
#	D.D.S. gets translated to DDS and coded (as it should).  But D.D.S. is not in abbrev.json. How is it reformatted?
#
#	drop html lines
#
#	sent_tokenize often breaks a line at Mrs. Mr.  Dr. U.S. etc.; fixed, but other abbreviations cause problems
#
#	drop articles (the, a, an) from text and from ngrams.json?
#	probably better to keep articles but use POS to disambiguate noun job from verb (e.g., cook, guide)
#		or drop articles (the, a, an) from text and from ngrams.json?
#
#	collect and analyze all the "ab bigrams" from the a X b matches: more mistakes or true finds?
#
#	optimize; python program was written to get the work done, not optimized
#
#	if a bigram or trigram is coded as ambiguous or not a ngram title (30801-30804), 
#		then don't count anything as found so that the later words can be used for the next match
#
#	is there  a better program to singularize words than inflect?
#		work around now identifies ~200  words that should not be singularized, e.g., boss, bus
#			and changes the inflect default using the inflect routine defnoun
#	punctuation: 
#		' :	's is now a separate word (e.g., Harper's agent-> " 's agent" = 500, performer's agent)
#			s' ???
#			confectioners' sugar
#			n't should be replaced with " not"
#	how to handle text files with non-ASCII character codes
#	identify (& drop?) headings for newspapers (multiplies "writer" etc.)?
#		do not code lines: BYLINE
#	expand the industrial sector ngramtitles/ codes
#		expand the government code to specific government agencies
#	edit the ridiculously long military ngramtitles in ngrams.json
#
# PLURALS:
#
# DISAMBIGUATION:
#	many ngrams have different meanings (codes) if capitlized or not
#		a. occupations are often also last names; these are coded only if lower case (e.g., farmer, carpenter;  see notTitle.txt)
#		b. other ngrams are coded only if capitalized (e.g., General, Ford, Marine, Northwestern, Daily News;  see notLower list  below)
#		c. other ngrams are coded only if all the letters are capitalized (e.g., SAT, NOW, SNAP;  see allUpper list below)
#		d. some ngrams are coded differently if capitalized or not (e.g., Vice President, Queens ;  see bothUL below)
#			school names also fall under this bothUL category since there are separate codes for named schools (capitalized) and schools in general (lower case)
#		all of these ambiguous ngrams are identified by a negative code in ngrams.json
#			when the program detects a negative code, it checks the lists of ngrams in notTitle, notLower, allUpper and the dicts bothUL for the proper disambiguation.
#			the ngram must be found in one of these lists or dicts
#
#		magazines: Working Mother, Parenting, add to notTitle?
#		add plural to some capitalization tests
#			e.g., justices is same as Justice, Generals, Marines
#			e.g., Hicks is likely a name; Hick is not
#		ambiguities, more than one possible code, mostly coded into 310xx : 
#			band, crew, driver, Georgia, intern, officer, page, partner, producer, team,
#		ambiguities, coded into most common code::
#			attendant		(4650= personal care, not a wedding ceremony attendant, nor attendant issues0
#			blood donor		(4650= personal care, not a volunteer blood donor)
#			bouncer			(3930= e.g., a club bouncer, not 9996 a bouncer hit in baseball)
#			broker			(4920= real estate broker, not 4820 investment broker )
#			caretaker		(4250= grounds caretaker, not 4610= personal caregiver) ???
#			carver			(2600= artist, not 8710, cutting worker)
#			cast			(2700= actors, not to cast aspersions etc.)
#			collector		(2400= archivists)
#			critic			(2005= experts, advisors, not journalist)
#			dishwasher		(16101, the appliance, not the restaurant worker, 4140; but "dish washer"= 4140)
#			floor manager	(30= legislator, not 4010 food service manager) MID not WK
#			hostess			(4151= a restaurant hostess, not a hostess at home)
#			General			(9800= military officer, not in general))
#			Indian			(13356= country; not Native American Indian)
#			king			(19= monarch; not chess piece or playing card)
#			minister		(2040= clergy; not government minister)
#			owner			(3288= business owner; not owner of euqipment, house, etc.)
#			painter			(2600= artist; not construction worker)
#			porter			(4350= a luggage carrier; not the beer))
#			principal		(-3288= likely manager & professional, uppercase= school principal) lots of false positives: loan principal, principal x)
#			queen			(19= monarch; not chess piece or playing card or Queen Anne furniture)
#			sailor			(9300= hired seaman, not a sailboat sailor; nor a US Navy sailor)
#			servant			(4650= personal care, not servant of the people or servant of God)
#			scout			(9812= military, rank ns: not to scout, not baseball scout)
#			sitter			(4600= baby sitter, child care worker is most common but also =4900, artists/photographer sitter, or chair sitter, fence sitter)
#			stringer		(2610= reporter, news stringer; not factory stringer)
#			union			(11190= labor union, not Union Army, many others)
#			vendor			(4965= sales people, not corporations selling something)
#		ambiguities, coded into less specific, overall code:
#			director		(3280= professional managerial, nec)
#		ambiguities, coded into 3288= larger prof/mgr code that captures only one meaning
#			associate		(-3288= likely prof/mgr, not ..associates with..)
#			aide, associate, backer, owner, staff, staff member
#		ambiguities, coded as ngram titles, but some are volunteer, hobby, nonpaid work:
#			7800 baker, 
#			4650 blood donor, 
#			4650 chaperone, 
#			7529 diver, 
#			6100 fisherman, 
#			4250 gardeners (4250= a landscape worker, not the home gardener), 
#			7750 fitter, 
#			     party host/ hostess
#		ambiguities, coded as volunteer, hobby, unpaid work, but sometimes a job
#			10360 hunter
#		nurses and aides= ?
#		election workers, poll watchers?
#		
#		black, white, poor, rich etc. [ambigwords] disambiguated if 1st word of quadgram: if people code follows, then = social group.
#
#		need pos tagger; some ngrams only if the word is a noun: cf. "to xxx"
#			broker, butcher, count, cast, cook, guide, host
#		pos tagger would also be useful for:
#			work
#		should some plurals be recognized as a separate code? eg. spouses=couple spouse=individual
#			and some plurals should not be coded: counts, royalties
#			some words would specify jobs/positions mainly in the plural: academics
#		all caps words have been changed to titles (e.g. COOPER = Cooper)
#

import re
import json
import sys

# there should be one and only one argument in calling Python
Nargs= len(sys.argv)
if Nargs<2:
	print("You need to call ngrams.py with an argument giving the filename prefix")
	print("	e.g., python3 ngrams.py NYT")
	print("	exiting...")
	sys.exit()
else:
	prefix= sys.argv[1]
	print("prefix: ", prefix)

# inflect will singularize words in text
#	it's not very good and requires several fixes.
import inflect
inf=inflect.engine()

# to strip html code from text:
from bs4 import BeautifulSoup

# to split text file into sentences
import nltk
from nltk import sent_tokenize, word_tokenize
from nltk import PorterStemmer, LancasterStemmer
porter = PorterStemmer()
lancaster = LancasterStemmer()


#
# xxxJobs.txt: dropped 28 Oct 2022
# after processing each text, writes a line for every ngram title found; 
#	this is now probably an unnecessary output file (& long)
ngramfile= prefix + "ngrams.txt"
ngramsf= open(ngramfile, "w")

####################################
# read list of filenames of input texts such as files with movie plots, newspaper articles, other texts...
infilelist= prefix + "files.txt"
files=open(infilelist).read()
# files is a long string with all file names:
# number of files:
textfiles=files.split('\n')
Ntextfiles=len(textfiles)

# strip off end of file line:
textfiles=textfiles[0:Ntextfiles-1]

outlogfile= prefix + "log.txt"
outlog= open(outlogfile, "w")

print ('\nList of text files to be analyzed: ' + infilelist + " " + str(type(textfiles)) + ", #files= " + str(len(textfiles)) + '\n')
outlog.write ('\nList of text files to be analyzed: ' + infilelist + " " + str(type(textfiles)) + ", #files= " + str(len(textfiles)) + '\n')

####################################
# read file of words that are incorrectly singularized by inflect.singular_noun
#	e.g., waitress, boss, chorus, police
#	also includes words that will not be singularized which are titles mainly when plural (e.g., sales)
dontsing= open("nosingularize.txt").read()
# dontsing is a long string with many end of line characters:
dontsing=dontsing.split('\n')
# number of 1-word lower case unigrams  not to be singularized:
Ndontsing=len(dontsing)
# strip off end of file line:
dontsing=dontsing[0:Ndontsing-1]
print ('dontsing (unigram titles not singularized)= ' + str(type(dontsing)) + ' Nlines=' + str(len(dontsing)))
outlog.write ('\ndontsing (unigram titles not singularized)= ' + str(type(dontsing)) + ' Nlines=' + str(len(dontsing)))
#
#
# read file of words in nosingularize.txt that are actual plurals:
#	e.g., minorities
plurals= open("plurals.txt").read()
# plurals is a long string with many end of line characters:
plurals=plurals.split('\n')
# number of 1-word lower case unigram titles not to be singularized:
Nplurals=len(plurals)
# strip off end of file line:
plurals=plurals[0:Nplurals-1]
print ('plurals (unigram titles already plural)= ' + str(type(plurals)) + ' Nlines=' + str(len(plurals)))
outlog.write ('\nplurals (unigram titles already plurals)= ' + str(type(plurals)) + ' Nlines=' + str(len(plurals)))
#

####################################
# contractions to be expanded (easier just to expand all "n\'t" to " not"; misses ain't, can't, shan't, won't, only can't and won't deserve separate replaces.
#notwords= [ 'ain\'t', 'aren\'t', 'can\'t', 'couldn\'t', 'didn\'t', 'doesn\'t', 'don\'t', 'hadn\'t', 'hasn\'t', 'haven\'t', 'isn\'t', 'mustn\'t', 'needn\'t', 'oughtn\'t', 'shan\'t', 'shouldn\'t', 'wasn\'t', 'weren\'t', 'won\'t', 'wouldn\'t' ]
#
####################################
# words that change meaning when capitalized or lower case:
#	all have negative code values in ngrams.json
#		the inverted code is the usual occ code; otherwise 31991(notLower), 31992(notTitle), 31993(allUpper), or dict value for bothUL
#	bothUL, bothUL2, bothUL3  have different codes for uppercase titles and lower case words (e.g., College)
#	notTitle unigram words are now read in from an external file that is easier to maintain
#
notLower4= ['general agreement on tariff']
notLower3= ['general agreement on']
# NB white house begins with "white" which will be disambiguated
notLower2= ['act up', 'central park', 'daily news', 'demand justice', 'east coast', 'national diet', 'the time', 'west coast', 'white house']
notLower= ['bayside', 'bush', 'count', 'del', 'dem', 'flushing', 'ford', 'general', 'grant', 'id', 'ill', 'ivies', 'major', 'marine', 'occidental', 'pierce', 'polish', 'pvt', 'rice', 'reunion', 'roe', 'snap', 'speaker', 'startout', 'surrogate', 'trump', 'tuft' ]
#
# readfile of notTitle words
#	notTitle are words (unigrams) that are usually unigram  titles only when lower case (e.g., carpenter, dean, mason, machine tool builder)
# NB rich is in notTitle.txt and will be disambiguated if lower case
innotTitle=open("notTitle.txt").read()
# innotTitle is a long string with all notTitle words :
notTitle=innotTitle.split('\n')
# number of notTitle words:
NnotTitle=len(notTitle)
# strip off end of file line:
notTitle=notTitle[0:NnotTitle-1]
print ('notTitle (unigram titles only when lowercase)= ' + str(type(notTitle)) + ' Nlines=' + str(NnotTitle) )
outlog.write ('\nnotTitle (unigram titles only when lowercase)= ' + str(type(notTitle)) + ' Nlines=' + str(NnotTitle) )
# add for trigrams and bigrams:
#	Working Mother?
#notTitle2= ["smarter living", "state college", "'s cook"] state college now in bothUL2
notTitle2= ["smarter living", "'s cook"]
notTitle3= ['machine tool builder']
notTitle4= ['machine tool builder association']

#
# these are unigram titles when allcaps but something else if not all caps:
#	IT, DO were dropped because found so often in all-cap title meaning "it" not "information technology"
#allUpper= ['ACT', 'AL', 'DA', 'COO', 'CORE', 'DE', 'ERA', 'FAIR', 'ICE', 'IMAN', 'IN', 'INS', 'IRA', 'IT', 'LA', 'LIU', 'MI', 'MIT', 'MO', 'NOW', 'OH', 'OR', 'PAC', 'RIT', 'SAT', 'SC', 'SES', 'SIU', 'SNAP', 'ST', 'US', 'USA', 'VA', 'WEAL', 'WHO']
allUpper=  ['ai', 'aim', 'act', 'al', 'da', 'coo', 'core', 'de', 'era', 'fair', 'glad', 'ice', 'iman', 'in', 'ins', 'ira', 'it', 'la', 'liu', 'mi', 'mit', 'mo', 'now', 'oh', 'or', 'pac', 'rit', 'sat', 'sc', 'ses', 'siu', 'snap', 'st', 'us', 'usa', 'va', 'weal', 'who']

# ambiguous tokens that can be disambiguated immediately by following token or, failing that, by total text context at end of text:
#	todo: disambiguate XXX of color where XXX precedes rather than follows the ambiguous word (person of color rather than black person)
#ambigwords= ["black","white","rich","richer","richest","poor","poorer","poorest"]
ambigwords= ["black", "colored", "minority", "white", "rich", "richer", "richest", "aging", "old", "older", "poor","poorer", "poorest", "gay"]
#	not ambiguous: African American, Negro, nonwhite
#ambigbigrams= ["of color"]
#	ambiguous bigrams of color have to be coded according to *previous* word, a significant rewrite
#ambigtrigrams= ["black and white", "white and black"]
#	not ambiguous: black and brown,  black or brown, brown and black, brown or black
#
# bothUL4= quadgrams that are coded differently depending on capitalization;
#	dict value is for upper case title 
#	default is lower case (-ngramcode)
#
#	todo fix: easier if key was (negative of) ngramcode value, not text since serveral texts have same ngramcode code
#
# School of Public Policy 13947, named school of public policy	/ -13957 any public policy school
bothUL4= {
 "school of public policy ":13947,
 }

# bothUL3: dict value is for upper case title			/ default (-code) is for lower case:
# School of Business 13945, named Business School		/ -13955 any school of business
# School of Law: 13942, named Law School				/ -13952 any law school
# School of Management 13945, named Business School		/ -13955 any business school
# School of Medicine 13940, named school of medicine	/ -13950 any medical school
# Public Policy School 13947, named school ofpub policy	/ -13957 any public policy school

#	? School of Theology

bothUL3= { 
 "county community college":13001,
 "junior high school":13005,
 "public policy school":13947,
 "right to life": 17056,
 "school of business": 13945,
 "school of law": 13942,
 "school of management": 13945,
 "school of medicine": 13940,
 "senior high school": 13004,
 "state community college": 13001
 }

# bothUL2: dict value is for upper case title			/ default (-code) is for lower case:
#	Business School 13945, named Business School		/ -13955 any school of business
#	CART driver": 2720 (race car driver)				/  -9750 (transportation labor)
#	Community College" 13001, (named Community College)	/ -10462, (general, any community college)
#	Dental School 13941, named Dental School			/ -13951 any school of dentistry
#	Divinity School 13944, named Divinity School		/ -13954 any seminary, divinity school
#	East Coast": 19763, (East Coast region)				/ -19773 (east coast of)
#	Elementary School" 13005, (named Elementary School)	/ -10454, (general, any elementary school)
#	Graduate School 13943, named Graduate School		/ -13950 any graduate school, programm
#	Grade School" 13005, (named Grade School)			/ -10454, (general, any Grade school)
#	High School" 13004, (named High School)				/ -10458, (general, any high school)
#	Intermediate School" 13005, (named Intermediate School)			/ -10456, (general, any Intermediate school)
#	Community College" 13001, ( Community College)		/ -10462, (general, any community college)
#	Law School: 13942, named Law School					/ -13952 any law school
#	Medical School 13940, named Medical School			/ -13950 any medical school
#	Metropolitan Area 10072, named Metro Area			/ -10062 metro area (general)
#	Middle School" 13005, (named Middle School)			/ -10456, (general, any middle school)
#	New School" 13374, (named New School, in NY))		/ -10450, (general, any new school)
#	Old Navy":31970, (not an old code)					/ -14130 (navy)
#	OR tech":3420, (health technicians)					/  -1965 (science technicians)
#	Prep School" 13003, (named Prep School)				/ -10457, (general, any prep school)
#	Public School" 13005, (named Public School)			/ -10454, (general, any grade school)
#	Secondary School" 13004, (named Secondary School)	/ -10458, (general, any secondary school)
#	State College" 31473, ambiguous State College 		/ -10461, (general, any state college)	/	
#	Theological Seminary 13944, named Seminary			/ -13955 any seminary
#	The Commons": 31907, (a place)						/ -17331 (the common good)
#	The President": 12, (the elected president)		/	-10 (ceo)
#	Vice President": 19500, (the elected vp)			/	-430 (manager)
#	West Coast": 19764, (West Coast region)				/ -19774 (west coast of)
#
# dict value is for upper case title / default (-code) is for lower case:
#	& what if one word is title and the other lower???
bothUL2= { 
 "business school": 13945,
 "cart driver":  2720,
 "community college": 13001,
 "concerned citizen": 20200,
 "county college": 13001,
 "dental school": 13941,
 "divinity school": 13944,
 "elementary school": 13005,
 "grade school": 13005,
 "graduate school": 13943,
 "grammar school": 13005,
 "high school": 13004,
 "intermediate school": 13005,
 "junior college": 13001,
 "junior high": 13005,
 "law college": 13942,
 "law school": 13942,
 "liberal party": 11425,
 "medical college": 13940,
 "medical school": 13940,
 "metro area": 10062,
 "metropolitan area": 10062,
 "middle school": 13005,
 "new school": 13374,
 "old navy": 31970,
 "or tech": 3420,
 "or technician": 3420,
 "prep school": 13003,
 "primary school": 13005,
 "public school": 13005,
 "public schools": 13006,
 "secondary school": 13004,
 "senior high": 13004,
 "state college": 31473,
 "state university": 13000,
 "theological seminary": 13944,
 "theological school": 13944,
 "the commons": 31907,
 "the president": 12,
 "vice president": 19500,
 "vision america": 11216,
 }

# bothUL= words that are coded differently depending on capitalization;
#	default (-ngramcode) is for lower case:
#	dict value is for upper case title				/ then for default lower case:
#					upper case dict value 				lower case default (-ngramcode)
#	Black":			15039, (race/name chk context)	/ -15038, (maybe race, check next token)
#	Boilermaker":	13116, (Purdue)					/  -6210, (makes boilers)
#	College"		13000, (named College)			/ -10460, college": (general, any college)
#	Commons"		31907, (a place, House of..))	/ -17331, commons": (the commons)
#	Community"		10079, (named Commmunity)		/ -10069, community": (general, any community)
#	County			10070, County": (named County)	/ -10060, (any county)
#	City"			10071, City": (named City)		/ -10061, (any city)
#	Democrat"		11420, (Democrat(ic) Party)		/ -17320, democrat(ic)": (democracy advocate)
#	District"		10075, District" (named) 		/ -10065, (any district)
#	East"			19763, (East Region)			/ -19773, east direction
#	God":			16840, God						/ -16841, (any god)
#	Justice":		 2110, Justice (a judge)		/ -17319, justice (concept)
#	Midweest"		19769, (Midwest Region)			/ -19779, midwestern direction ???
#	President":		   12, (e.g., US President)		/    -10, (chief execs)
#	Principal":		  232 (school principal)		/  -3288, principal": (general, likely prof/mgr)
#	North"			19761, (North Region)			/ -19771, north direction
#	Northeast"		19765, (Northeast Region)		/ -19775, northeast direction
#	Northwest"		19766, (Northwest Region)		/ -19776, northwest direction
#	Queens"			14801, (a NY borough)			/    -19, queens": (royalty)
#	Representative":   30, (legislator, in Congress)/  -3288, (likely prof/mgr)
#	School":		13005, (named School)			/ -10450, (general, any school)
#	Schools":		13006, (named School District)	/ -10451, (general, schools)
#	Secretary":		   16, (govt, cabinet Secretary)/  -5700, (clerical)
#	Smart":			31903, (person's name)			/ -10430, smart
#	South"			19762, (South Region)			/ -19772, south direction
#	Southeast"		19767, (Southeast Region)		/ -19777, southeast direction
#	Southwest"		19768, (Southwest Region)		/ -19778, southwest direction  ?? often Southwest Airlines
#	Town"			10066, (named Town)				/ -10076, town": 
#	Township"		10066, (named Township)			/ -10076, township"
#	University		13000, (named University)		/ -10460, university": (general, any university) 
#	VA		"		     , (Veterans Admin)			/ -     , virginia": 
#	Village"		10068, (named Village)			/ -10078, village": (village)
#	West"			19764, (West Region)			/ -19774, west direction
#	White":			15116, (likely name)			/ -15118, (maybe race)
#
#	dropped: too ambiguous, now 31703, Hunter: could bn 13071 (Hunter College); or a name? / or hunter: -10360 (recreational sports)
#
#	? Associate
#	? LIU, Liu

# bothUL1: dict value is for upper case title 
#	upper case (dict value) even if in title, because uppercase more common
#	todo: fix Eastern, Northern, etc. which are usually not a region, but a school name
bothUL1= {
 "democrat": 11420,
 "democratic": 11420,
 "east": 19763,
 "eastern": 19783,
 "midwest": 19769,
 "midwestern": 19789,
 "north": 19761,
 "northern": 19771,
 "northeast": 19765,
 "northeastern": 31451,
 "northwest": 19766,
 "northwestern": 13026,
 "republican": 11410,
 "south": 19762,
 "southern": 19782,
 "southeast": 19767,
 "southeastern": 31600,
 "southwest": 19768,
 "southwestern": 19788,
 "west": 19764,
 "western": 19784
 }
# upper case (dict value) if not lower case or if in title (default negative key) 
bothUL= {
 "associate": 31800,
 "boilermaker": 13116,
 "college": 13000,
 "community": 10079,
 "commons": 31907,
 "county": 10070,
 "city": 10071,
 "depression": 17274,
 "district": 10075,
 "god": 16840,
 "justice": 2110,
 "president": 12,
 "principal": 230,
 "queens": 14801,
 "representative": 30,
 "school": 13005,
 "schools": 13006,
 "secretary": 16,
 "seminary": 13944,
 "smart": 31903,
 "town": 10076,
 "township": 10076,
 "university": 13000,
 "village": 10078,
 }


####################################
# readfile of occupation (& other) titles (mostly from US Census):
codes= open("codes.json").read()
# codes.json is a long string, make codes.json into a dict, codelabels:
codelabels= json.loads(codes)
print ('\ncode labels (e.g, occs 2010 titles from Census+)= ' + str(type(codelabels)) + ' Nlines=' + str(len(codelabels)) )
outlog.write ('\ncode labels (e.g., occs 2010 titles from Census+)= ' + str(type(codelabels)) + ' Nlines=' + str(len(codelabels)) )
#
# readfile of unigram  titles (e.g. jobtitles  from US Census):
ngrams= open("ngrams.json").read()
# ngrams is a long string, make unirgrams into a dict, unigram labels:
ngramlabels= json.loads(ngrams)
print ('\nngram labels (e.g., jobtitles mostly from Census+)= ' + str(type(ngramlabels)) + ' Nlines=' + str(len(ngramlabels)) )
outlog.write ('\nngramlabels (jobtitles mostly from Census+)= ' + str(type(ngramlabels)) + ' Nlines=' + str(len(ngramlabels)) )
# separate ngrams.json into 4 dicts (1-word, 2-word, 3-word, or 4-word ngrams) for testing texts:
ngrams1= {}
ngrams2= {}
ngrams3= {}
ngrams4= {}
for ngram in ngramlabels:
	Nwords= len(ngram.split())
	if Nwords==1:
		ngrams1[ngram]=ngramlabels[ngram]
	elif Nwords==2:
		ngrams2[ngram]=ngramlabels[ngram]
	elif Nwords==3:
		ngrams3[ngram]=ngramlabels[ngram]
	elif Nwords==4:
		ngrams4[ngram]=ngramlabels[ngram]
print ('	ngrams1 (one-word ngrams)= ' + str(type(ngrams1)) + ' Nlines=' + str(len(ngrams1)))
outlog.write ('\n	ngrams1 (one-word ngrams)= ' + str(type(ngrams1)) + ' Nlines=' + str(len(ngrams1)))
print ('	ngrams2 (two-word ngrams)= ' + str(type(ngrams2)) + ' Nlines=' + str(len(ngrams2)))
outlog.write ('\n	ngrams2 (two-word ngrams)= ' + str(type(ngrams2)) + ' Nlines=' + str(len(ngrams2)))
print ('	ngrams3 (three-word ngrams from)= ' + str(type(ngrams3)) + ' Nlines=' + str(len(ngrams3)))
outlog.write ('\n	ngrams3 (three-word ngrams)= ' + str(type(ngrams3)) + ' Nlines=' + str(len(ngrams3)))
print ('	ngrams4 (four-word ngrams)= ' + str(type(ngrams4)) + ' Nlines=' + str(len(ngrams4)))
outlog.write ('\n	ngrams4 (four-word ngrams)= ' + str(type(ngrams4)) + ' Nlines=' + str(len(ngrams4)))

# check for occ labels for each ngram code:
#	otherwise ngrams.py doesn't fail until after going through all the texts.
for ngram in ngramlabels:
	ngramcode= ngramlabels[ngram]

####################################
# readfile of abbreviations to be replaced:
#
#	should all single letters+dot be changed to just the single letter; most are middle initials, should not cause an end of sentence.
#
abbrevfile= open("abbrev.json").read()
abbrevdict= json.loads(abbrevfile)
#
print ('\nabbreviations to be replaced by full words= ' + str(type(abbrevdict)) + ' Nlines=' + str(len(abbrevdict)))
#print (abbrevdict.keys())
print ('\n')
outlog.write ('\n	abbreviations to replace= ' + str(type(abbrevdict)) + ' Nlines=' + str(len(abbrevdict)))
#outlog.write ('\n' + abbrevdict.keys())
#
# store (disambiguated) ngramcode code for each ngramlabel found across all texts:
ngramcodes= {}

####################################
# output files:
#
# xxxCodes.xls:
# main output: after processing each text file, writes one record for each occ2010 found, regardless of "job" title
#	blank line at beginning of each text
#	writes as tab delimited file for input into spreadsheet/ stats program
codesfile= prefix + "Codes.xls"
codesf= open(codesfile, "w")
codesf.write ("filename	" + "OccCode	" + "Nocc	" + "Nplurals	" + "Occlabel\n" )
#
# xxxTexts.xls:
# after processing each text, writes a count of #words, #sentences, etc., one line per text
	# results for each file:
	#Ntitles Nmentions Nsentences Nwords Npara
textsfile= prefix + "Texts.xls"
textsf= open(textsfile, "w")
textsf.write ("ifile	filename	Ntitles	Nmentions	Npara	Nsentences	Nwords	Nbytes")
#
# xxxkwic.txt:
# writes key-word-in-context file: a sentence for every "job" title found in the text
#	useful for checking code accuracy
#	also is input to subsequent program to analyze sentiment or other characteristics about the "occ"
#	if a sentence has more than one "job" title, the kwic sentence is written for each "job" title
kwicfile= prefix + "kwic.txt" 
kwic= open(kwicfile, "w")
#
# xxxkwic2.txt: (now dropped)
# includes a second kwic file using the preprocessed sentence rather than a sentence close to the original.
#	kwicfile2 is good for further natural language processing
#kwicfile2= prefix + "kwic2.txt" 
#kwic2= open(kwicfile2, "w")
#
# xxxTotals.txt;
# after processing all texts, writes totals for each occ2010 and the jobs found in that occ2010
# file created below after processing all texts.
####################################
#
#	end of file inputs
#
####################################
# initializing jobs.py variables
# Sum...  and N... are totals across all files 
#
Sumtitles=0
Sumpara=0
Sumsentences=0
Sumwords=0
Sumcodecounts= {}
Sumcodeplurals= {}
Ntextscodes= {}
Sumngramcounts= {}
Sumjobplurals= {}
Ntextsjob= {}
ifile=0
for file in textfiles:
	ifile= ifile+1 # at end should = len(textfiles)
	# write text file name to ...Codes.txt file:
	codesf.write ("\n" + file + ":\n" )
	ngramsf.write ("\n" + file + ":\n" )
	kwic.write ("\n" + file + ":\n" )
	#kwic2.write ("\n" + file + ":\n" )
	# write blank line to ...Codes.txt file:
	codesf.write ("\n")
	foundjobs= []
	Nfound= [0]
	Nplural= [0]
	jcensus= [0]
	ingram=0
	# todo: work with different codings
	text0=open(file, encoding = "ISO-8859-1").read()
	#text0=open(file).read()
	# drop html:
	text1= BeautifulSoup(text0, features="html.parser")
	textstring= text1.get_text()
	Nbytes=len(textstring)
	#print ("\n" + file + ":\n" + str(textstring))
	#Nwords=textstring.count(" ")
	#print ("\n" + file + ":\n" + str(textstring) + "\nNwords= " + str(Nwords))
	#
	# add end of paragraph marker (2 end of lines together) because the sentence tokenizer will ignore paragraphing:
	textstring=re.sub(r'(\w)\n\n', r'\1.\nThis is an EOP.\n', textstring)
	textstring=re.sub(r'(\W)\n\n', r'\1\nThis is an EOP.\n', textstring)
	#
	#	drop newlines to make one long text:
	textstring=textstring.replace('\n', ' ')
	#
	# 9 Aug 2018: delete hyphens
	#	hyphens are probably meaningless only grammatical distinctions between e.g., working-class and working class
	#	also will match 3-word hypthenated phrases that get lost when making hyphen a separate word (e.g., child - care aide)
	textstring=textstring.replace('-',' ')
	#	but a couple of exceptions:
	textstring=textstring.replace('x ray','x-ray')
	textstring=textstring.replace('pre k','pre-k')
	#textstring=textstring.replace('teen ager','teen-ager')
	#
	# drop indentations in NYTimes:
	textstring=textstring.replace('\xa0','')
	textstring=textstring.replace('AN A','')
	#
	Nwords=textstring.count(" ")
	#print ("\n" + file + ":\n" + str(textstring) + "\nNbytes=" + str(Nbytes) + " " + "Nwords= " + str(Nwords))
	#
	for abbrev in abbrevdict:
		# drop the if?
		if abbrev in textstring:
			textstring= textstring.replace(abbrev,abbrevdict[abbrev])
			#print ('	', file, abbrev, abbrevdict[abbrev])
	#
	#	U.S. after U.S.A.
	textstring= textstring.replace("U.S.","US")
	#
	# U.S.C. is often a cite to UScode.  Otherwise USC is usually University of Southern California
	textstring= re.sub(r'([0-9]) USC ', r'\1 USCode', textstring)
	#
	# a single upper case letter followed by a period and another space is usually an initial in a name; this drops the period so it won't confuse sentencing.
	textstring= re.sub(r' ([A-Z])\. ', r' \1 ', textstring)
	#
	# reduce multiple blanks to a single blank
	textstring= re.sub(" +", " ", textstring)
	#
	# make each sentence a new string
	#	sent_tokenize often broke a line at Mrs. Mr. Dr. U.S. etc.; fixed 5 June 2021
	textlines= sent_tokenize(textstring)
	#
	# process each sentence in the file:
	Npara=0
	iline=0
	Nambig=0
	for line0 in textlines:
		#print (str(line0) + "\n")
		iline=iline+1
		lineambig={}
		foundcensus=0
		# drop EOP marker:
		if "This is an EOP." in line0:
			Npara=Npara+1
		line=line0.replace('This is an EOP.', '')
		# 
		# these replaces are done line by line (rather than for the whole textlines file) so that the kwic file line (line0) looks more like the original
		#
		# all upper case lines are probably titles; change to title in order to avoid hits of allUpper words:
		if line.isupper():
			line= line.title()
		# 
		# periods only at tend of line kept as separate word
		line=re.sub('\.$', ' \.', line)
		#	otherwise periods are abbreviations that have not caused sent_tokenize to break the line:
		#	these non-problematic abbreviations are coded in ngrams.json without periods
		#		so they are dropped from the line
		#		? replace with a space instead?
		line=re.sub('\.', '', line)
		# EOL is just an extra "word" at the end of the line so that the last trigram includes a real word to test as the first (2nd to last) word
		line=re.sub('$', ' EOL ', line)
		# replace commas with a space
		#		enables long title with a comma to be handled correctly (University of California, Berkeley)
		line=line.replace(',',' ')
		# footnotes in wikipedia plot texts:
		line=line.replace('[',' [ ')
		line=line.replace(']',' ] ')
		# punctuation (except hyphens) becomes a separate word:
		#	easier (& better?) to drop [punctuation.
		#line=line.replace(',', ' , ') dropped June 2022, commas now replaced with a space
		#line=line.replace('.',' .')
		line=line.replace('/',' / ')
		line=line.replace('|',' | ')
		line=line.replace('?',' ?')
		line=line.replace('!',' !')
		line=line.replace(';',' ;')
		line=line.replace(':',' :')
		line=line.replace('>',' > ')
		line=line.replace('(',' ( ')
		line=line.replace(')',' ) ')
		line=line.replace('\*',' \* ')
		# replace ', 's, and "
		line=line.replace('\"',' \" ')
		line=line.replace("\'\'",' \" ') # some files use '' for "
		line=line.replace('\'',' \' ')		# apostrophes become separate word 
		# so, xxxs' becomes xxxs '
		line=line.replace(' \' s ',' \'s ')	# except apostrophe s which is its own word
		#
		# reduce multiple blanks to a single blank
		line= re.sub(" +", " ", line)
		#
		# initialize in order to create initial quadgrams, tri-grams, bigrams that won't match any job title
		#	there must be a more efficient method of analyzaing the beginning of a line than this kludge
		# wordnewU is exactly how it was in the text
		wordfirstU='X'
		word2U='X'
		word3U='X'
		wordnewU='X'
		# wordnewS is after singularizing the word, exc if wordnewU.lower() is in the list of nosingularize.txt
		wordfirstS='x'
		word2S='x'
		word3S='x'
		wordnewS='x'
		pluralfirst=0
		plural2=0
		plural3=0
		pluralnew=0
		census=0
		wordbiU= wordfirstU + ' ' + word2U 
		wordbi2U= wordfirstU + ' ' + word3U   # skip word2U to see if surrounding words are a jobtitle/ code
		wordbi3U= word2U     + ' ' + word3U   # if wordbi2U is a jobtitle then make sure wordbi3U is not
		wordtriU= wordfirstU + ' ' + word2U + ' ' + word3U
		wordquadU= wordfirstU + ' ' + word2U + ' ' + word3U + ' ' + wordnewU
		# skipword is a flag to note a word has already been included in trigram, bigram
		skipword=0
		# create list of words for this line:
		linelist= line.split(' ')
		iwordline=0
		for wordnewU in linelist:
			# problems with inflect singular_noun:
			#	inflect.singular_noun wrongly singularizes many words, esp those ending in "ss", e.g, waitress, class,
			#		so, jobs.py needs 200+ lines of code (defnoun) above to fix those mistakes
			#	IT = (Information Technology) but also = it which is the singular of they,them, etc. 
			#		& so gets coded a lot, but not filtered out by IT must be in caps; 
			#		so IT now dropped from ngrams.json
			iwordline += 1
			pluralnew= 1
			if wordnewU.lower() in dontsing: # wordnewU in list not to singularize
				wordnewS= wordnewU
				pluralnew=0
				if wordnewU.lower() in plurals: # wordnewU in nosingularize list that is an actual plural
					pluralnew=1
				#print ('Dont singularize ', wordnewU, ': ', line)
			else:
				#print (wordnewU)
				wordnewS= inf.singular_noun(wordnewU)	# wordnewS= singular root of wordnewU (maintains case)
				if not wordnewS:  # wordnewU already singular
					pluralnew=0
					wordnewS=wordnewU
			#wordnewLstem= lancaster(wordnewS.lower())
			# 
			# form quadgram, trigram and bigrams with [singularized] new word
			wordquadU= wordfirstU + ' ' + word2U + ' ' + word3U + ' ' + wordnewU
			wordquadS= wordfirstS + ' ' + word2S + ' ' + word3S + ' ' + wordnewS
			wordquad= wordquadS.lower()
			#plural= pluralnew  plural not needed, uses pluralnew
			# form trigram and bigrams with [singularized] new word
			wordtriU= wordfirstU + ' ' + word2U + ' ' + word3U
			wordtriS= wordfirstS + ' ' + word2S + ' ' + word3S
			wordtri= wordtriS.lower()
			#plural= pluralnew  plural not needed, uses pluralnew
			#
			wordbiU= wordfirstU + ' ' + word2U
			wordbiS= wordfirstS + ' ' + word2S
			wordbi=  wordbiS.lower()
			#plural= plural2  plural not needed, will use plural2
			#
			# wordbi2 picks up bigram job titles with a word in between
			wordbi2U= wordfirstU + ' ' + word3U
			wordbi2S= wordfirstS + ' ' + word3S
			wordbi2=  wordbi2S.lower()
			#plural= pluralnew   plural not needed, will use pluralnew
			#
			# wordbi3 not processed here but needed to prevent wordbi2 from processing
			wordbi3S= word2S + ' ' + word3S
			wordbi3=  wordbi3S.lower()
			#plural= pluralnew   plural not needed, will use pluralnew
			#
			wordfirst= wordfirstS.lower()	# wordfirst is lower case and singularized
			#plural= pluralfirst  plural not needed, will use pluralfirst
			#
			# program goes through 5 main searches for a code quadgram (1,2,3,4),  trigram(1,2,3), bigram(1+2), bigram2(1+3), and firstword(1)
			if skipword<1 and wordquad in ngrams4:
				skipword= 4
				census= ngrams4[wordquad]
				# check whether this job quadgram is an exception:
				if census<0:		# check for notTitle etc.
					census= -census 			# default is actual code, the negative of the value in ngrams.json
					#if wordquad in allUpper:	# no quadgrams in allUpper
					if wordquad in notLower4: 	# e.g., general agreement on tariff
						if wordquad.islower():	# not the code category
							census= 31991 		# not a code, original is lower case, probably not an occ =31991
							skipword=0
							#wordquad= wordquad.lower()
						else:
							#census= -census	# already the default value
							wordquad= wordquad.title()  # change to capitalized ("General Agreement On")
					elif wordquad in notTitle4: 	# Machine Tool Builders Association
						if wordquadU.islower() or iline==1 or iwordline==4:	# original is lower case or first(title) line, so probably an occupation
							#census= -census				# changed above to the negative of what is stored in ngrams.json)
							wordquad= wordquad.lower()	# redundant, kept only for code symmetry
						else:
							census= 31992  					# not a code, original is capitalized, probably not an occ =31992
							skipword=0
							wordquad= wordquad.title()	# change to capitalized ("Machine Tool Builder")
					elif wordquad in bothUL4:  		# 4. no bothUL4 yet
						if wordquadU.islower():		# original is lower case, so use -census, as in default above
							#or iline==1			# even if title, more likely to be capitalized version (e.g. Named State Community College)
							#census= -census			# changed above to the negative of what is stored in ngrams.json)
							wordquad= wordquadS.lower()		# redundant, kept only for code symmetry
							if census==9999:			# or tech: keep searching, don't skip second word of trigram
								skipword=0
						else:
							census= bothUL4[wordquad]  # get alternate value from key of wordquad
							wordquad= wordquad.title()		# change to capitalized (but becomes Or Tech and Cart Driver, not OR tech and CART driver!)
				# check whether this job quadgram has already been found for this file:
				if wordquad in foundjobs:
					# quadgram has been found before in this file, so just increment count
					ifound= foundjobs.index(wordquad)+1
					Nplural[ifound]= Nplural[ifound]+pluralnew
					Nfound[ifound]= Nfound[ifound]+1
				else:
					# quadgram has not been found before in this file, so add to list of jobs found
					ingram=ingram+1
					ifound= ingram
					Nfound.append(1)
					Nplural.append(pluralnew)
					jcensus.append(census)
					foundjobs.append(wordquad)
				# census >= 31900 are excluded categories 
				if census>0 and census<31900:
					foundcensus+=1
				# write this job quadgram (whether new or not)
				# writes the line close to the original format (line0) , before most replacements (line).
				# print (file + "	" + str(iline) + "	" + str(iwordline) + "	" + str(ifound) + "	4	" + "	" + str(pluralnew) + "	" +str(census) + "	" + wordquadU + "	" + line0 + "\n")
				kwic.write (file + "	" + str(iline) + "	" + str(iwordline) + "	" + str(ifound) + "	4	" + str(pluralnew) + "	" +str(census) + "	" + wordquadU + "	" + line0 + "\n")
			#
			#
			# next, check if first 3 words == any trigram job titles
				# only check if wordtri not in an earlier quadgram
			elif skipword<1 and wordtri in ngrams3:
				skipword= 3
				census= ngrams3[wordtri]
				# check whether this job trigram is an exception:
				if census<0:		# check for notTitle etc.
					census= -census 			# default is actual code, the negative of the value in ngrams.json
					#if wordtri in allUpper:	# no trigrams in allUpper
					if wordtri in notLower3: 	# General Agreement on
						if wordtri.islower():	# not the code category
							census=31991
							skipword=0
							#wordtri= wordtri.lower()
						else:
							#census= -census	# already the default value
							wordtri= wordtri.title()  # change to capitalized ("General Agreement On")
					elif wordtri in notTitle3: 	# Machine Tool Builders Association
						if wordtriU.islower() or iline==1 or iwordline==4:	# original is lower case or first(title) line, so probably an occupation
							#census= -census				# changed above to the negative of what is stored in ngrams.json)
							wordtri= wordtri.lower()	# redundant, kept only for code symmetry
						else:
							census= 31992  					# not a code, original is capitalized, probably not an occ =31992
							skipword=0
							wordtri= wordtri.title()	# change to capitalized ("Machine Tool Builder")
					elif wordtri in bothUL3:  		# 4. e.g., vice president, OR tech, CART driver
						if wordtriU.islower():		# original is lower case, so use -census, as in default above
							#or iline==1			# even if title, more likely to be capitalized version (e.g. Named State Community College)
							#census= -census			# changed above to the negative of what is stored in ngrams.json)
							wordtri= wordtriS.lower()		# redundant, kept only for code symmetry
							if census==9999:			# or tech: keep searching, don't skip second word of trigram
								skipword=0
						else:
							census= bothUL3[wordtri]  # get alternate value from key of wordtri
							wordtri= wordtri.title()		# change to capitalized (but becomes Or Tech and Cart Driver, not OR tech and CART driver!)
				# check whether this job trigram has already been found for this file:
				if wordtri in foundjobs:
					# trigram has been found before in this file, so just increment count
					ifound= foundjobs.index(wordtri)+1
					Nplural[ifound]= Nplural[ifound]+pluralnew
					Nfound[ifound]= Nfound[ifound]+1
				else:
					# trigram has not been found before in this file, so add to list of jobs found
					ingram=ingram+1
					ifound= ingram
					Nfound.append(1)
					Nplural.append(pluralnew)
					jcensus.append(census)
					foundjobs.append(wordtri)
				# census >= 31900 are excluded categories 
				if census>0 and census<31900:
					foundcensus+=1
				# print this job trigram (whether new or not)
				#	prints line close to the original format (line0) , before most replacements (line).
				kwic.write (file + "	" + str(iline) + "	" + str(iwordline) + "	" + str(ifound) + "	3	" + str(pluralnew) + "	" +str(census) + "	" + wordtriU + "	" + line0 + "\n")
			#
			#
			# next, check if first 2 words of trigram == any bigram job titles
				# only check if wordbi has not been part of an earlier trigram
			elif skipword<1 and wordbi in ngrams2:
				skipword=2
				census= ngrams2[wordbi]
				if census<0: 	# negative ngrams.json code requires special handling:
					census= -census					# default code (e.g., for lower case in notTitle2) is negative of the ngrams.json code
					if wordbi in notLower2:    	# 1. e.g., "national diet, daily news"
						if wordbiU.islower():			# word is a not a title (first letter capitalized) then usually not an occupation 
							census= 31991  					# if all lower, then probably not an occ =31991
							skipword=0
						else:
							#census=-census					# changed above to negative of ngrams.json code 
							wordbiS= wordbi.title()		# if all caps, then make it a title (problem for US)
					elif wordbi in notTitle2: 		# Smarter Living, State College [PA]
						if wordbiU.islower() or iline==1 or iwordline==4:	# original is lower case or first(title) line, so probably an occupation
							#census= -census				# changed above to the negative of what is stored in ngrams.json)
							wordbi= wordbi.lower()	# redundant, kept only for code symmetry
						else:
							census= 31992  					# original is capitalized, probably not an occ =31992
							skipword=0
							wordbi= wordbi.title()	# change to capitalized ("State College")
					#elif wordbi in allUpper:    	# 3. no bigrams in allUpper
					elif wordbi in bothUL2:  		# 4. e.g., vice president, OR tech, CART driver
						if wordbiU.islower() :	# original is lower case, so use -census, as in default above
							#or iline==1			# even if title, more likely to be capitalized version (e.g. Vice President)
							#census= -census		# changed above to the negative of what is stored in ngrams.json)
							wordbi= wordbiS.lower()	# redundant, kept only for code symmetry
							if census==9999:		# or tech: keep searching, don't skip second word of bigram
								skipword=0
						else:
							census= bothUL2[wordbi]  # get alternate value from key of wordbi
							wordbi= wordbi.title()		# change to capitalized (but becomes Or Tech and Cart Driver, not OR tech and CART driver!)
				# check whether this job bigram has already been found for this file:
				if wordbi in foundjobs:
					# bigram has been found before in this file, so just increment count
					ifound= foundjobs.index(wordbi)+1
					Nplural[ifound]= Nplural[ifound]+plural2
					Nfound[ifound]= Nfound[ifound]+1
				else:
					# bigram has not been found before in this file, so add to list of jobs found
					ingram=ingram+1
					ifound= ingram
					Nfound.append(1)
					Nplural.append(plural2)
					jcensus.append(census)
					foundjobs.append(wordbi)
				# census >= 31900 are excluded categories 
				if census>0 and census<31900:
					foundcensus+=1
				# print this job bigram (whether new or not)
				kwic.write (file + "	" + str(iline) + "	" + str(iwordline) + "	" + str(ifound) + "	2	" + str(plural2) + "	" +str(census) + "	" + wordbiU + "	" + line0 + "\n")
			#
			# next, check if first & 3rd words of trigram == any bigram job titles
				# don't count a match if word2 is in ambigwords
				# don't count a match if word2 + word3 is a bigram even if word1 + word3 is a bigram 
				# 	will pick up word2 + word3 match in next loop
				# only check if wordbi2 has not been part of an earlier trigram
			elif skipword<1 and wordbi2 in ngrams2 and wordbi3 not in ngrams2 and wordfirstS.lower() not in ambigwords:
				skipword=3
				census= ngrams2[wordbi2]
				if census<0:  # e.g., vice xxx president, or xxx tech, cart xxx driver
					census= -census					# default code (for lower case) is negative of the ngrams.json code
					if wordbi2 in notLower2:    	# 1. e.g., "nationbal diet"
						if wordbi2.islower():			# word is a not a title (first letter capitalized) then usually not an occupation 
							census= 31991  					# if all lower, probably not an occ =31991
							skipword=0
						else:
							#census=-census					# changed above to negative of ngrams.json code 
							wordbi2= wordbi2.title()	# if all caps, then make it a title (problem for US)
					elif wordbi2 in notTitle2: 		# 2. Smarter Living, State College, but Smarter X Living is not the magazine, so treat as smarter x living
						if wordbiU.islower() or iline==1 or iwordline==4:	# original is lower case or first(title) line, so probably an occupation
							#census= -census				# changed above to the negative of what is stored in ngrams.json)
							wordbi2= wordbi2.lower()	# redundant, kept only for code symmetry
						elif wordbi2 == "'s cook":
							census= 31992  					# original is capitalized, probably not an occ =31992
							skipword=0
							wordbi2= wordbi2.title()	# change to capitalized ("'s x Cook") usually Cook is a last name 
						else:
							#census= -census				# changed above to the negative of what is stored in ngrams.json)
							wordbi2= wordbi2.lower()	# redundant, kept only for code symmetry
					#elif wordbi2 in allUpper:    	# 3. no bigrams in allUpper
					elif wordbi2 in bothUL2:  		# 4. e.g., vice xxx president, OR xxx tech, CART xxx driver
						#census= 9999				#	don't use key value, not likely to be a occ at all
						#            	 			#	use default -census value
						skipword=0
				# check whether this job bigram has already been found for this file:
				if wordbi2 in foundjobs:
					# bigram has been found before in this file, so just increment count
					ifound= foundjobs.index(wordbi2)+1
					Nplural[ifound]= Nplural[ifound]+plural2
					Nfound[ifound]= Nfound[ifound]+1
				elif skipword>0:
					# bigram has not been found before in this file, so add to list of jobs found
					ingram=ingram+1
					ifound= ingram
					Nfound.append(1)
					Nplural.append(plural2)
					jcensus.append(census)
					foundjobs.append(wordbi2)
				# census >= 31900 are excluded categories 
				if census>0 and census<31900:
					foundcensus+=1
				# print this job bigram (whether new or not)
				#	this will print erroneous vice xxx president etc., but too few to worry about
				#	kwic code 6 indicates a bigram from 1st and 3rd words of a trigram
				#	these "bigrams" have a higher error rate than a true bigram
				kwic.write (file + "	" + str(iline) + "	" + str(iwordline) + "	" + str(ifound) + "	6	" + str(plural2) + "	" +str(census) + "	" + wordbi2U + "	" + line0 + "\n")
			#
			#
			# finally, check if first word of quadgram == any unigram job title
				# if quadgram, trigram and bigram are not a job title, check whether the first word in the trigram is a job:
				#	(2nd word will become first word in next bigram & will be checked then)
				#	except if 1st word has been part of the previous trigram or bigram (skipword>=1)
			elif skipword<1 and wordfirst in ngrams1:	# wordfirst is lower case and singularized
				skipword==1
				census= ngrams1[wordfirst]    # wordfirst is sigularized and lower case
				# 
				# census code <0 => wordfirst is ambiguous but can be disambiguated based on capitalization:
				#	testing wordfirst for allUpper not needed since an all Upper line above translated to .title() 
				#if wordfirstU.isupper():			# if wordfirstU is all upper case => usually an article title; translate to proper name titled and process
					# a couple of exceptions: DA, COO, etc.:
					#if wordfirstS.lower() in allUpper:			# for these special all uppercase jobs (DA etc.) keep wordfirst as all upper case
						#wordfirst= wordfirstS.upper()			# make wordfirst all upper case singular, not all lower case singular
					#else: 
						#wordfirstS= wordfirstS.title()		# translate wordfirstS to proper name as best guess; wordfirst remains lower case
				if census<0:
					census=-census			# default code is the negative of what is stored
					# separate entries for upper case / lower case titles in foundjobs:
					#	default jobtitle in foundjobs is capitalized (title)
					#  do this when first seen as wordnew?
					#  originally isupper() code was here, after census<0
					if wordfirst in notLower:			# 1. e.g., "general", "justice"  words where lower case is usually not an occupation (exc. some plurals)
														#	but generals, justices, (plurals) are occupations;  they are filtered out by notsingular.txt
						if wordfirstU.istitle():			# word is a title (first letter capitalized) then usually an occupation (-census above)
							#census=-census					# changed above to negative of ngrams.json code 
							wordfirst= wordfirst.title()	# if all caps, then make it a title (problem for US)
						else:
							census= 31991  					# if not capitalized, probably not an occ =31991
					elif wordfirst in notTitle: 		# 2. e.g., "Potter", "Packer", "Rich" and nosingularized "Queens", "Kings"
						if wordfirstU.islower() or iline==1 or iwordline==4:	# original is lower case or first(title) line, so probably an occupation
							#census= -census				# changed above to the negative of what is stored in ngrams.json)
							wordfirst= wordfirstS.lower()	# redundant, kept only for code symmetry
						else:
							census= 31992  					# original is capitalized, probably not an occ =31992
							wordfirst= wordfirst.title()	# change to capitalized
					elif wordfirst in allUpper:    		# 3. e.g., DA, US, COO; coded only if all upper, otherwise a different word, 31993
						if census==18840:  # US=18840 / us=17605
							if wordfirstS.isupper():
								census=18840
							else:
								census=17605
						elif census==14330:  # VA (Veterans Admin)=14330 / Va (Virginia)=19746 but VA can also be postal code for Virginia
							if wordfirstS.isupper():
								census=14330
							else:
								census=19746
						elif wordfirstS.isupper():
							#census=census	# (default code -- the negative of what is stored in ngrams.json)
							wordfirst= wordfirst.upper()
						else:
							census= 31993   # if not all upper case, then probably not an occ = 31993
							#wordfirst= wordfirst.lower()
					elif wordfirst in bothUL:    		# 4. e.g., president, college
						if wordfirstU.islower() or iline==1 or iwordline==4:			# original is lower case or title of doc, so use alternative value from key
							#census= -census					# changed above to the negative of what is stored in ngrams.json)
							wordfirst= wordfirstS.lower()		# redundant, kept only for code symmetry
						else:
							census= bothUL[wordfirst]  		# get dict value		
							wordfirst= wordfirst.title()	# change (back) to capitalized
					elif wordfirst in bothUL1:    		# 4b. e.g., republican, democrat Usually the party when in article title.
						if wordfirstU.islower():			# original is lower case, so use alternative value from key
							#census= -census					# changed above to the negative of what is stored in ngrams.json)
							wordfirst= wordfirstS.lower()		# redundant, kept only for code symmetry
						else:
							census= bothUL1[wordfirst]  		# word is Upper case (even if in title) get dict value		
							wordfirst= wordfirst.title()	# change (back) to capitalized
					else:
						print ("	ERROR: negative code " + str(census) + " not resolved: " + wordfirst + " in " + file)
						outlog.write ("\n	ERROR: negative code " + str(census) + " not resolved: " + wordfirst + " in " + file)
				#
				#	process if wordfirst is an word to be disambiguated (e.g., black, white, poor, rich)
				#		check if next word(s) are a valid (or even ambiguous) code
				#
				if wordfirstS.lower() in ambigwords:
					nextcensus= 0
					next3= word2S.lower() + ' ' + word3S.lower() + ' ' + wordnewS.lower()
					if next3 in ngrams3:
						nextcensus= ngrams3[next3]
						#print (wordfirst + next3 + ' ' + str(nextcensus))
					else:
						next2= word2S.lower() + ' ' + word3S.lower() 
						if next2 in ngrams2:
							nextcensus= ngrams2[next2]
							#print (wordfirst + next2 + ' ' + str(nextcensus))
						else:
							next1= word2S.lower() 
							if next1 in ngrams1:
								nextcensus= ngrams1[next1]
								#print (wordfirst + next1 + ' ' + str(nextcensus))
							else:  # next 3,2,or 1 tokens are not a census code, so ambiguous wordfirst may not be a code either
							       # 	so, will have to check total text file context
							       # 	dropped; incrementing ambig code by one signals a need to check total text context
								nextcensus= 0
								#census= census+1
					# 30000-30999+ are objects, not persons, jobs, jobs, etc.
					# 31000-31899 are ambiguous, possibly persons, jobs, etc.
					# census >= 31900 are excluded categories 
					# census < 0 are negative codes that signal disambiguation by lower case (job) or upper case (name, not a job)
						# for here we will assume that whether a name or a job, the ambiguous word is a social group describing the code
					if (nextcensus>-30000 and nextcensus<30000) or (nextcensus>31000 and nextcensus<31900):
						# ambiguous word followed by person, job, etc., so probably a coded category (black, poor, etc.)
						census= census-8
						#print (wordfirst + next3 + ' ' + str(nextcensus) + ' ' + str(census))
					#elif nextcensus>0 and nextcensus<30900:	# ambiguous token is followed by person(nextcensus<30800) and so was indeed a code 
						#census= census-8
						#print (wordfirst + next3 + ' ' + str(nextcensus) + ' ' + str(census))
					#else:								# ambiguous token is not followed by a person, so it's still ambiguous
						# leave census as is (nnnn8) for ambigwords without following code
						#census= census+1
						#print (wordfirst + next3 + ' ' + str(nextcensus) + ' ' + str(census))
				# either jobtitle not ambiguous (census>0) or after disambiguation:
				#	then check whether this single-word job has already been found for this file:
				if wordfirst in foundjobs:
					# wordfirst has been found before in this file, so just increment count:
					ifound= foundjobs.index(wordfirst)+1
					Nfound[ifound]= Nfound[ifound]+1
					Nplural[ifound]= Nplural[ifound]+pluralfirst
				else:
					# word has not been found before in this file, so add to list of jobs found
					ingram=ingram+1
					ifound= ingram
					Nfound.append(1)
					Nplural.append(pluralfirst)
					jcensus.append(census)
					foundjobs.append(wordfirst)  # wordfirst has been disambiguated 
				if census>0 and census<31900:
					foundcensus+=1
				# print this line (whether job is new or not)
				kwic.write (file + "	" + str(iline) + "	" + str(iwordline) + "	" + str(ifound) + "	1	" + str(pluralfirst) + "	" +str(census) + "	" + wordfirstU + '	' + line0 + "\n")
		####################################################################################
		# end of processing this 4gram:
		# 
		#for wordnewU in linelist:
			#elif skipword<1 and wordfirst in ngrams1:	# wordfirst is lower case and singularized
			#if skipword<1 and wordquad in ngrams4:
			# reset 1st 2nd and 3rd words in quadgram:
			wordfirstU=word2U
			wordfirstS=word2S
			pluralfirst=plural2
			word2U=word3U
			word2S=word3S
			plural2=plural3
			word3U=wordnewU
			word3S=wordnewS
			plural3=pluralnew
			if skipword>0:
				skipword= skipword-1
		####################################################################################
		#
		# end of processing all words in this line (for wordnewU in linelist:)
		# disambiguate some codes (e.g., black, poor, )
		#	if a job or person type is also in the sentence, then ambiguous title is probably referring to a person
		iwordline= iwordline-2
	####################################################################################
	# 
	# end of processing all lines in the file (for line0 in textlines)
	# 	print results of this file:
	Ntitles=len(Nfound)-1
	Nmentions= sum(Nfound)
	Nsentences=len(textlines) - Npara
	#Nwords= Nwords+Nsentences-Npara
	#Nwords= Nwords+Nsentences
	Nwords= Nwords - 4*Npara
	#Nsentences=Nsentences-1
	Npara=Npara
	textsf.write ("\n" + str(ifile) + "	" + file + "	" + str(Ntitles) + "	" + str(Nmentions) + "	" + str(Npara) + "	" + str(Nsentences) + "	" + str(Nwords) + "	" + str(Nbytes) )
	if ifile % 100 ==0:
		print (str(ifile) + "	" + file + "	#jobtitles=" + str(Ntitles) + "	#mentions=" + str(Nmentions) + "	# paragraphs=" + str(Npara) + 	"	#sentences=" + str(Nsentences) + "	#words=" + str(Nwords) )
	#
	# accumulate totals across files
	Sumsentences= Sumsentences+Nsentences
	Sumpara= Sumpara+Npara
	Sumwords= Sumwords+Nwords
	Sumtitles= Sumtitles+Ntitles
	ingram=0
	censuscounts={}  	#	#mentions of this census code in this text file
	censusplurals={}	#	#plurals of this census code in this text file
	for job in sorted(foundjobs):	# list job titles alphabetically
		ingram=foundjobs.index(job)+1
		# write to text file X job title output:
		#	tabs make this easy to import into stata, excel:
		ngramsf.write (file + '	' + str(ingram) + '	#mentions=	' + str(Nfound[ingram]) + '	#plurals=	' + str(Nplural[ingram]) + "	census=	" + str(jcensus[ingram]) + '	' + job + "\n")
		# accumulate totals by job title across text files:
		if job in Sumngramcounts:
			Sumngramcounts[job]= Sumngramcounts[job] + Nfound[ingram]
			Sumjobplurals[job]= Sumjobplurals[job] + Nplural[ingram]
			Ntextsjob[job]= Ntextsjob[job] + 1
		else:
			Sumngramcounts[job]= Nfound[ingram]
			Sumjobplurals[job]= Nplural[ingram]
			Ntextsjob[job]= 1
			ngramcodes[job]= jcensus[ingram]  # store disambiguated census code for this job ngram
		# accumulate totals by census code across job titles for this text file:
		if jcensus[ingram] in censuscounts:
			censuscounts[jcensus[ingram]] = censuscounts[jcensus[ingram]] + Nfound[ingram]
			censusplurals[jcensus[ingram]] = censusplurals[jcensus[ingram]] + Nplural[ingram]
		else:
			censuscounts[jcensus[ingram]] = Nfound[ingram]
			censusplurals[jcensus[ingram]] = Nplural[ingram]
	for code in sorted(censuscounts):
		# write text file totals to ..Census.txt file:
		codesf.write (file + "	" + str(code) + "	" + str(censuscounts[code]) + "	" + str(censusplurals[code]) + "	" + codelabels[str(code)] + "\n" )
		# accumulate totals by census code for all files:
		if code in Sumcodecounts:
			Sumcodecounts[code]= Sumcodecounts[code] + censuscounts[code]
			Sumcodeplurals[code]= Sumcodeplurals[code] + censusplurals[code]
			Ntextscodes[code]= Ntextscodes[code] + 1
		else:
			Sumcodecounts[code]= censuscounts[code]
			Sumcodeplurals[code]= censusplurals[code]
			Ntextscodes[code]= 1

print (" ")
outlog.write (" ")
# end of python text search; print total files processed

print ("# files= " + str(ifile) + "=" + str(len(textfiles)) + "	# titles=" + str(Sumtitles) + " # sentences=" + str(Sumsentences) + " # words=" + str(Sumwords) )
outlog.write ("\n# files= " + str(ifile) + "=" + str(len(textfiles)) + "	# titles=" + str(Sumtitles) + " # sentences=" + str(Sumsentences) + " # words=" + str(Sumwords) )

# create and write Totals.txt
totalsfile= prefix + "Totals.txt"
totalsf= open(totalsfile, "w")
totalsf.write ("\n    	N	 plurals	Ntexts	code	jobtitle")
# loop over all jobs within (census)codes
for code in sorted(Sumcodecounts):
	totalsf.write ("\n" + str(code) + "=	" + str(Sumcodecounts[code]) + "	" + str(Sumcodeplurals[code]) + "	" + str(Ntextscodes[code]) + "	" + codelabels[str(code)] + "\n")
	for ngram in sorted(Sumngramcounts):
		if ngramcodes[ngram]==code:
			totalsf.write ("	" + str(Sumngramcounts[ngram]) + "	" + str(Sumjobplurals[ngram]) + "	" + str(Ntextsjob[ngram]) + "	" + str(ngramcodes[ngram]) + "	" + ngram + "\n")

totalsf.write ("\n# titles=" + str(Sumtitles) + "\n# files=" + str(len(textfiles)) + "\n# sentences=" + str(Sumsentences) + "\n# words=" + str(Sumwords) + "\n" )
outlog.write  ("\n# titles=" + str(Sumtitles) + "\n# files=" + str(len(textfiles)) + "\n# sentences=" + str(Sumsentences) + "\n# words=" + str(Sumwords) + "\n" )

