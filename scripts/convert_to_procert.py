import jsonlines
from bs4 import BeautifulSoup

# def parse_page_info(page_info: dict) -> dict:
#     """
#     Parse the page_info dictionary to convert HTML strings to BeautifulSoup objects.
    
#     Args:
#         page_info (dict): The dictionary containing page information with HTML strings.
    
#     Returns:
#         dict: The updated dictionary with BeautifulSoup objects.
#     """
#     # FIXME: Note to handle the Amendment No. for standard code
#     standard_code = page_info['standard_code']['code']
#     if ':' in standard_code:
#         standard_code, version_no= standard_code.split(':')
#     standard_status = page_info['standard_code']['status']

def parse_element(obj):
    """
    Parse the element to extract text and handle nested elements.
    
    Args:
        element (BeautifulSoup element): The BeautifulSoup element to parse.
    
    Returns:
        str: The extracted text from the element.
    """
    amendments_no = []

    # Handle the slash
    if "/" in obj['standard']['code']:
        split_element = obj['standard']['code'].split('/')
        obj['standard']['code'] = split_element[0]
        for ele in split_element[1:]:
            if "AC" or "corrigendum" not in ele:
                amendments_no.append(ele)

    # Amendment No
    if "+" in obj['standard']['code']:
        split_element = obj['standard']['code'].split('+')
        obj['standard']['code'] = split_element[0]
        for ele in split_element[1:]:
            if "AC" or "corrigendum" not in ele:
                amendments_no.append(ele)

    # Standard Code
    if ":" in (standard_code_:=obj['standard']['code']):
        standard_code, version_no =  standard_code_.split(':')
    else:
        standard_code, version_no = standard_code_, None

    # Standard Status
    status = obj['standard']['status']

    # Standard Name
    standard_name = obj['standard']['full_data']
    if ')' in standard_name:
        standard_name = standard_name[standard_name.index(')') + 1:]
    if obj['page_info']['date_table']:
        dow_date = obj['page_info']['date_table']["date of Withdrawal (DOW) (5)"]
        dop_date = obj['page_info']['date_table']["date of Publication (DOP) (4)"]
    else:
        dop_date, dow_date = None, None
    final_result = {
                    "standard_code": standard_code,
                    "version_no": version_no,
                    "status": status,
                    "standard_name": standard_name,
                    "amendments_no": amendments_no,
                    "dow_date": dow_date,
                    "dop_date": dop_date,
                    "full_standard_code": original_standard_code,
                    "url": f"https://standards.cencenelec.eu/dyn/www/{obj['standard']['url']}",
                    "original_query": obj["query"],
                    }
    return final_result


if __name__ == "__main__":
    import sys
    from bs4 import BeautifulSoup
    with jsonlines.open("./data/procert_format.jsonl", 'w') as f:
        with jsonlines.open("./data/pages_result.jsonl", 'r') as reader:
            for obj in reader:
                if not obj["page_info"]:
                    obj["page_info"] = None
                    print("No page info meet, ignore this standard code:", obj['standard']['code'], file=sys.stderr)
                    continue
                else:
                    page_info = {}
                    for k, v in obj["page_info"].items():
                        if v:
                            soup = BeautifulSoup(v, 'html.parser')
                            th = [x.text.strip() for x in soup.find_all('th')]
                            td = [x.text.strip() for x in soup.find_all('td')]
                            if th and td and len(th) == len(td):
                                info_dict = {x: y for x, y in zip(th, td)}
                                page_info[k] = info_dict
                        else:
                            page_info[k] = None
                    obj['page_info'] = page_info

                # f.write(obj)
                original_standard_code = obj['standard']['code']

                # try:
                final_result = parse_element(obj)
                f.write(final_result)
                # except AssertionError:
                #     print(original_standard_code, file=sys.stderr)
                # except Exception as e:
                #     print(original_standard_code, file=sys.stderr)


                
                    



                