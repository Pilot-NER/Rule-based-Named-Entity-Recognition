# importing external libraries
import csv
import re
import pprint
from GeoExtraction.geoextraction import GeoExtraction
from difflib import SequenceMatcher

# lists
memos_list = []
vendors_list = []

# dictionary
memo_to_vendor_dict = {}
with open("Sample memos - memos.csv", 'r') as memofile: #open dataset
    memo = csv.reader(memofile)
    next(memo)  # skip the first line
    for row in memo:
        memos_list.append(row[0])  # lists of memo (exclude vendors)
        vendors_list.append(row[1].lstrip('[\'').rstrip('\']'))  # lists of vendors
        memo_to_vendor_dict[row[0]] = row[1].lstrip('[\'').rstrip('\']')  # dictionary of memos mapped to vendors

# function to check similarity
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio() # compares similarity of a and b based on Gestalt pattern matching algorithm

# simplification function
def sim1(memos_list): #remove financial shorthand
    changed_list = []
    for i, mem in enumerate(memos_list):
        if len(mem.split()) <= 3: # memos less than or equal to three words are left alone
            changed_list.append('')
        else:
            shorthands = "(?i)debit card|credit card|debit|credit|card|crd|ref|cashier check purchase|paypal| NY | New York | Las Vegas | NV | San Francisco | SF | San Francis |San Mateo | San Jose | Port Melbourn | CA | JAMAICA | Sydney | NS | Log Angeles | AU | Surry Hills | Singapore | SG "
            mem = re.sub(' +',' ',re.sub(shorthands, '', mem)) #remove abbreviations listed in shorthands
            changed_list.append(mem) # append simplified memo to output list
    return changed_list

def sim2(memos_list): #reomve mixed alphanumerics
    num = "[^s]*\d\d\d\d\d+[^s]*"  # more than 5 numbers
    alt_alphanum = "(?i)[^s][a-z]+\d+\w*[^s]"  # alternating numbers and alphabets (alphabets come first)
    alt_alphanum_2 = "(?i)[^s]\d+[a-z]+\w*[^s]"  # alternating numbers and alphabets (numbers come first)
    L = list()
    for m in memos_list:
        # remove the string of numbers and alphanumeric strings from all the memos
        tmp = re.split(num + "|" + alt_alphanum + "|" + alt_alphanum_2, m) # split the string using the the string of numbers, the alphanumeric strings as separators
        tmp = [x.lstrip().rstrip() for x in tmp]
        tmp = ' '.join(tmp).lstrip().rstrip()
        # print(m, tmp)
        if tmp:
            L.append(tmp)
        else:   # if the memo string is entirely made up of alphanumeric strings or strings of numbers, add the entire memo back to the list.
            L.append('')
    return L

def sim3(memos_list): # remove the date from the string (assume format of date - "MM/DD")
    date = "[^\s]*\d\d/\d\d[^\s]*"  # date
    ref = "(?i)[^\s]*ref[\d^\s]*"  # reference number in format "REF...""
    crd = "(?i)[^\s]*crd[\d^\s]*"  # credit number in format "CRD..."
    new_list = []
    for i, memo in enumerate(memos_list):
        # remove the dates, reference numbers and credit numbers from the memo string
        # remove the dates
        tmp = re.split(date, memo)
        tmp = [x.lstrip().rstrip() for x in tmp]
        tmp = ' '.join(tmp).lstrip().rstrip()

        # remove the reference numbers
        tmp = re.split(ref, tmp)
        tmp = [x.lstrip().rstrip() for x in tmp]
        tmp = ' '.join(tmp).lstrip().rstrip()

        #remove the credit numbers
        tmp = re.split(crd, tmp)
        tmp = [x.lstrip().rstrip() for x in tmp]
        tmp = ' '.join(tmp).lstrip().rstrip()
        if tmp == memo:
            new_list.append('')
        else:
            new_list.append(tmp)
    return new_list

def sim4(memos_list): # ignore online/bank transfers
    changed_list = []
    for x in range(len(memos_list)):
        # if the memo string contains the word "internet transfer" or "online transfer", remove the memo string from the list.
        if 'internet transfer' in memos_list[x].lower():
            changed_list.append('')
        elif 'online transfer' in memos_list[x].lower():
            changed_list.append('')
        else: # the memo string does not contain the word "internet transfer" or "online transfer"
            changed_list.append(memos_list[x])

    return(changed_list)

def sim5(memos_list): # remove the last instance of * and anything before it
    sim_list = []
    for x in range(len(memos_list)):
        if '*' in memos_list[x]: # check if * exists
            sim_list.append(memos_list[x][memos_list[x].rfind('*')+1:]) # remove everything before and including the *
        else:
            sim_list.append('')
    return(sim_list)

def sim6(memos_list): # remove punctuation
    sim_list = []
    a = ['"',',','.']
    for x in range(len(memos_list)):
        # if any of the listed punctuation is present, delete it
        if any(i in memos_list[x] for i in a):
            temp = memos_list[x].replace('"', "")
            temp = memos_list[x].replace(',', "")
            sim_list.append(temp)
        else:
            sim_list.append('')
    return(sim_list)
    
# extraction patterns

def ext1(data_list): # anything in quotation marks = name
    match_list = []
    for x in range(len(memos_list)):
        matches=re.findall(r'\"(.+?)\"',memos_list[x]) # take everything between quotes
        if matches != [] and len(matches) == 1: # if the pattern exists
            match_list.append(matches[0]) # add what is between quotation marks to output list
        else:
            match_list.append('') # add Null to output list
    return(match_list) # return output list

def ext2(data_list): # repeated words = name
    rep_list = []
    for data in data_list:
        name =  ''
        words = data.split()
        counts = {}
        for word in words:
            if word not in counts:
                counts[word] = 1
            else:
                counts[word] += 1
                if counts[word] > 1:
                    name += word + ' '
        if not(name == ""):
            rep_list.append(name)
        else:
            rep_list.append('')
    return(rep_list)

def ext3(memos_list): # memo length <=3 >> whole memo = name
    name_list = []
    L_removed = []
    num_location = "[^\s]*\d\d\d[^\s]*|\sCA\s"  # numbers or "CA" california
    for i, m in enumerate(memos_list):
        tmp = m.split()
        if len(tmp) <= 3:
            tmp_s = re.sub(num_location, "", m)
            name_list.append(tmp_s.lstrip().rstrip())
            L_removed.append(i)
        else:
            name_list.append('')
    memos_list = [m for i, m in enumerate(memos_list) if i not in L_removed]
    return(name_list)

def ext4(memos_list): # word before company suffixes = name
    keywords = "(?i)\sinc.\s|(?i)\sLLC\s|(?i)\sCO\s|(?i)\sLimited\s|(?i)\sINC\s|(?i)\sCorporation\s|(?i)\s.com\s|(?i)\s.net\s"
    k = keywords.split("|")
    ans = list()
    new_memos = list()
    for m in memos_list:
        tmp = re.split(keywords, m)
        if len(tmp) > 1:
            ans.append(tmp[0])
        else:
            new_memos.append(m)
            ans.append('')
    return ans

def pend1(memos_list): # extract location terms
    new_memos, location_dict = list(), dict()
    G = GeoExtraction()
    count = 0
    for m in memos_list:
        l = G.extract_location(m)
        new_m = G.remove_location(m)
        new_memos.append(m)
        location_dict[new_m] = l
        print(count)
        count += 1
    return new_memos, location_dict

# creating output lists for each pattern
ori = ['memo']+memos_list

# simplify the patterns

def fix(memolist,my_list):
    outlist = my_list
    for x in range(len(memolist)):
        if my_list[x+1] == '':
            outlist[x+1] = memolist[x]
    return(outlist)

simp_list = sim6(ori)
simp_list = fix(memos_list,simp_list)
simp_list = sim5(ori)
simp_list = fix(memos_list,simp_list)
simp_list = sim4(ori)
simp_list = fix(memos_list,simp_list)
simp_list = sim3(ori)
simp_list = fix(memos_list,simp_list)
simp_list = sim2(ori)
simp_list = fix(memos_list,simp_list)
simp_list = sim1(ori)
simp_list = fix(memos_list,simp_list)

simp_list[0] = "simp"
sim1 = ['sim1']+sim1(memos_list)
sim2 = ['sim2']+sim2(memos_list)
sim3 = ['sim3']+sim3(memos_list)
sim4 = ['sim4']+sim4(memos_list)
sim5 = ['sim5']+sim5(memos_list)
sim6 = ['sim6']+sim6(memos_list)
ext1 = ['ext1']+ext1(simp_list[1:])
ext2 = ['ext2']+ext2(simp_list[1:])
ext3 = ['ext3']+ext3(simp_list[1:])
ext4 = ['ext4']+ext4(simp_list[1:])

# creating output list for failed extractions
extF = ['failed']
for x in range(len(ori)):
    if ext1[x] == ext2[x] == ext3[x] == ext4[x] == '':
        extF.append('')
    else:
        extF.append('extracted')

# function to check accuracy for each extraction (ignores lower/upper case diff)
def check_accuracy(ans_list,my_list):
    # change everything to lowercase
    l1 = [x.lower() for x in ans_list]
    l2 = [x.lower() for x in my_list]
    acc_list = []
    for x in range(len(ans_list)):
        if ans_list[x] == '':
            acc_list.append(0)
        else:
            acc_list.append(similar(l1[x],l2[x])) # append the similarity score
    return(acc_list)

# get the accuracy of all memos based on each extraction pattern
right_list = ["vendor"] + vendors_list

acc1_list = check_accuracy(right_list, ext1)
acc1_list[0] = 'accuracy'

acc2_list = check_accuracy(right_list, ext2)
acc2_list[0] = 'accuracy'

acc3_list = check_accuracy(right_list, ext3)
acc3_list[0] = 'accuracy'

acc4_list = check_accuracy(right_list, ext4)
acc4_list[0] = 'accuracy'

# extraction of vendor name
def extract(ori,simp_list,ext1,ext2,ext3,ext4): #extracting while prioritizing highest precision patterns first
    final_list = []
    noExt_list = []
    for x in range(len(ext1)):
        if len(ext1[x]) > 2 and ext1[x] != '':
            final_list.append(ext1[x])
        elif len(ext4[x]) > 2 and ext4[x] != '':
            final_list.append(ext4[x])
        elif len(ext2[x]) > 2 and ext2[x] != '':
            final_list.append(ext2[x])
        elif len(ext3[x]) > 2 and ext3[x] != '':
            final_list.append(ext3[x])
        elif len(simp_list[x]) > 2:
            final_list.append(simp_list[x])
        else:
            final_list.append('')
            noExt_list.append(ori[x])
    return(final_list,noExt_list)

final_output = extract(ori,simp_list,ext1,ext2,ext3,ext4)[0] # list of final output
noExt_list = extract(ori,simp_list,ext1,ext2,ext3,ext4)[1] # list of failed extractions
final_output[0] = 'output' # give final output list a title


acc_list = check_accuracy(right_list, final_output) #check accuracy of final output
acc_list[0] = 'accuracy' # give accuracy list a title

# tracking changes created by the pattern functions
csvfile = 'tracking.csv' #open file we use to record the tracking

with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for x in range(len(ori)): #write the change each pattern has on the memos
        writer.writerow([ori[x],sim1[x],sim2[x],sim3[x],sim4[x],sim5[x],sim6[x],simp_list[x],right_list[x],ext1[x],acc1_list[x],ext2[x],acc2_list[x],ext3[x],acc3_list[x],ext4[x],acc4_list[x],extF[x],final_output[x],acc_list[x]])