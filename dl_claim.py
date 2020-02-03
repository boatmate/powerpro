#!/usr/bin/env python3 -W ignore::DeprecationWarning
# -*- coding: utf-8 -*-





# runs with:
# file:///%appdata%\Notepad++\plugins\config\PythonScript\scripts\download_claims.py#1

# cmd /C cd "$(CURRENT_DIRECTORY)"&& conda activate sp && python -i "$(FULL_CURRENT_PATH)" NPPclaims
import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
    
# import logging
# logging.captureWarnings(True)
import warnings


from pathlib import Path  

tmp = Path(r"~\AppData\Local\Temp").expanduser()




def fxn():
    warnings.warn("deprecated", DeprecationWarning)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()
    import networkx as nx
    import spacy
    from subprocess import run, PIPE, CompletedProcess
    import regex, fire, os
    import regex_t
    import my_OPS
    import regex, json
    import pyperclip
    
# for communicating with python2.7 running in notepad++
# receive from raw_path       file:///%temp%\raw.txt#1
# send to res_path            file:///%temp%\res.txt#1
raw_path = os.path.join(os.getenv("temp"), "raw.txt")
res_path = os.path.join(os.getenv("temp"), "res.txt")

def g_claims_desc(cc, mainno, kc,  on_google = None, aka = None, part_kc=None):
    '''extract claims and description from patents.google.com or OPS'''
    if aka:
        cc, mainno, kc = aka
    response = run(["xidel","https://patents.google.com/patent/"+ cc + mainno + kc +"/en",
        "-e",'//claim!(.,"@@@"),//div[@class="claim"]/div[@class="claim-text"]!(.,"@@@")',
        "-e", '//section[@itemprop="description"]',
        "--download=c:/scripts/raw_google.txt"], 
        stderr=PIPE, stdout=PIPE, encoding='utf8' )
    # file:///c:/scripts/raw_google.txt#1
    if response.returncode==0:
        adict = {}
        description = response.stdout[int(response.stdout.rindex('@@@'))+4:]
        # import io
        # with io.open("description.google.txt",'w',encoding='utf8') as f:
            # f.write(description)
        if description:
            # print(cc, mainno, kc, "FOUND description on Google Patents")
            adict['description'] = description
        claimset= [(i, regex.sub(r"^(\n)", "", aclaim)) for i, aclaim in 
                    enumerate(response.stdout.split("@@@")[:-1])]
        if claimset:
            import io
            with io.open("claims.google.txt",'w',encoding='utf8') as f:
                f.write(str(claimset))
            numset = [x[0]+1 for x in claimset]
            claimset = [x[1] if regex.match(str(x[0]+1), x[1]) 
                        else str(x[0]+1)+". "+x[1] 
                        for x in claimset] 
            # add claim numbers if they are missing
            # spacy sentences = claims?
            # claimset = "".join(claimset).replace('\n\n', '\n')
            # print(cc, mainno, kc, "FOUND", len(numset), "claims on Google Patents")
            adict['claims'] = claimset
        return adict
    else:
        
        return my_OPS.get_claims_desc(cc, mainno, kc)
        
       
# print(g_claims_desc("EP","1449497","B1")["claims"])
# print(g_claims_desc("US","3467141", "A")["claims"])
 
 
 
# claim_list= [
# "1. A nozzle device wherein ",
# "2. The nozzle device of claim 1 wherein ",
# "3. The nozzle device of claim 1 or claim 2 wherein ",
# "4. The nozzle device of Claims 1-3 wherein ​",
# "5. The nozzle device of claims 1 - 3 and 4 wherein ",
# "6. The nozzle device of claims 1 to 2 and 4-5 wherein",
# "7. The nozzle device of claims 1, 2 and 3—5, and 6 wherein",
# "8. The nozzle device of any of one of the preceding claims wherein",
# "9. A different independent  method wherein",
# "10. The method of claim 9 wherein", 
# "11. The nozzle device of claim 5 wherein",
# "12. The nozzle device of claim 11 wherein",
# "13. A vacuum cleaner with a wand further comprising the nozzle of any one of Claims 1 to 8, 11 and 12 wherein"
# ]

 
def get_all_dominators(claim_list):
    '''Returns a dict containing a list of the dominator claims for each claim in the claim set. Used for antecedent analysis.''' 
    # nlp = spacy.load('en_core_web_sm')
    # doc = nlp("".join(claim_list))
    # for i, sent in enumerate(doc.sents):
        # print(sent.text)
        # print(claim_list[i])

 
    G = nx.DiGraph(pubnum="EP1234567")
    allnums = r"claims?((\d+|to|and|claims?|or|(?>[ ,~—;-]))+\d+)?"
    numranges = r"(\d+)( to | ?[-~—] ?)(\d+)"
    # curr_subject, curr_root = "", ""
    for i, cl in enumerate(claim_list):
        # first_nc = next(nlp(cl).noun_chunks)
        # print("**NPP", first_nc[1:])
        # looks_dependent = False
        # if first_nc.root.head.text == curr_root:
            # looks_dependent = True
            # print("EQ")
        # else:
            # curr_subject, curr_root = first_nc[1:], first_nc.root.head.text
            # print("NOTEQ",first_nc.root.head.text, curr_root)
        # print("curr_subject", curr_subject, "curr_root", curr_root)
        # print(cl.encode('utf8'))  #encode to allow pass to console of Python Script
        depset = []
        is_dep = regex.search(allnums, cl, flags=regex.IGNORECASE)
        if is_dep:
            # print(is_dep.group(0))
            # print(is_dep.group(1))
            has_range = regex.findall(numranges, is_dep.group(0))
            # print(has_range)
            if has_range:
                for x in has_range:
                    # print(" start/end", x[0], x[2])
                    depset += range(int(x[0]), int(x[2])+1)
                remain = regex.findall(r"\d+", regex.sub(numranges, "", is_dep.group(0)))
            else:
                remain = regex.findall(r"\d+", is_dep.group(0))
            # print("   remain:", remain)
            if is_dep.group(1):
                for y in remain:
                    # print("   adding:", y)
                    depset += [int(y)]
            else:
                for ct in range(i):
                    depset += [ct+1]
        depset = [(x, i+1) for x in depset]
        # print("depset:", sorted(depset), "\n")
        if depset:
            G.add_edges_from(depset)
        else:
            G.add_node(i+1)
    # print(G.number_of_nodes())
    all_dominators = {}
    for indep_claim in [n for n,d in G.in_degree() if d==0]:
        subset_dic = nx.immediate_dominators(G, indep_claim)
        for each_clm in sorted(subset_dic.keys())[::-1]:
            this_one = subset_dic[each_clm]
            ss = [this_one]
            while True:
                if this_one == indep_claim:
                    break
                else:
                    this_one = subset_dic[this_one]
                    ss.append(this_one)
            # print(ss, each_clm, this_one == indep_claim,  this_one)
            all_dominators.update({each_clm : ss})
    return all_dominators
 
 
    
# print(get_all_dominators(claim_list))  EP1449497B1
 
def NPPclaims():
    # point of entry
    # file:///%temp%\res.txt#1
    claimset = []
    with open(raw_path,'r') as f:
        data = json.load(f)
        if isinstance(data, dict):
            # print("Ok we have a dict with the claim list", data)
            # print here breaks the json std out
            claimset = data['claims']
        elif isinstance(data, str):
            print ("We must use text to extract a pub number" , data)
            from_clip = list(regex_t.get_pubs(data).values())[0]
            if from_clip:
                claimset = g_claims_desc(**from_clip)["claims"]
                if claimset:
                    data = {}
                    data["claims"] = claimset
        if claimset:       
            dom = get_all_dominators(claimset)
            if dom:
                data.update({"dominators" : dom})
                data.update({"indeps" : 
                                list(k for (k,v) in dom.items() if k in v)})
            # this becomes the stdout
            print(json.dumps(data, indent=4))
            with open(res_path,'w',encoding='utf8') as f:
                f.write(json.dumps(data, indent=4))
            
            # print("".join([x for i, x in enumerate(data["claims"], 1) 
                                                # if i in data["indeps"]]))

def elsewhere(cc, mainno, kc,  on_google = None, aka = None, part_kc=None, file=None, start_page=None, **kwargs):
    claimset = g_claims_desc(cc, mainno, kc)["claims"]
    if claimset:
        data = {}
        data["claims"] = claimset
        dom = get_all_dominators(claimset)
        if dom:
            data.update({"dominators" : dom})
            data.update({"indeps" : 
                                list(k for (k,v) in dom.items() if k in v)})
            # print(json.dumps(data, indent=4))
            # with open(res_path,'w',encoding='utf8') as f:
                # f.write(json.dumps(data, indent=4))
            
            print("".join([x for i, x in enumerate(data["claims"], 1) 
                                                if i in data["indeps"]]))
            old =  cc+mainno+kc+"\r\n"                                      
            pyperclip.copy(old + "".join([x for i, x in enumerate(data["claims"], 1) 
                                                if i in data["indeps"]]))                                   
        return data


rx = regex.compile(r"(?P<cc>[A-Z]{2})"
                   r"(?P<no>(?:(?<=JP)[HS])?(?:(?<=TW)M)?\d+)"
                   r"(?:[\(_]?)" 
                   r"(?P<kc>[A-Z]\d?)")

def pubnum_split(x):
    match = rx.search(x)
    if match:
        return (match.group('cc'), match.group('no'), match.group('kc'))
    else:
        return (None, None, None)
        

def ind_claims_ff(open_it = True):
    '''main entry point
    
    starts after ps_utilex.txt generated from powerpro using:
    
    file.writeall(?"%temp%/ps_utilex.txt", win.exename (win.mainunder) ++ "\n" ++ win.caption("=PDFXCView") ++ "\n" ++ win.caption("c=MozillaWindowClass"))
    file.runwait(0, ?"%py_sp%", ?"-i C:\scripts\ps_utilex.py open_tab")
'''
    _exe, _pdf_capt, _ff_capt = (tmp/"ps_utilex.txt").read_text().splitlines()
    # file:///c:\Users\PHILIP~1\AppData\Local\Temp\ps_utilex.txt#1
    if _exe == "firefox":
        cc, no, kc = pubnum_split(_ff_capt)
        if cc:
            elsewhere(cc, no, kc)
        else:
            print("firefox bottom bumped but pub num not matched in:")
            print(_ff_capt)



if __name__ == '__main__':
    fire.Fire()
  
# NPPclaims() 
 
 