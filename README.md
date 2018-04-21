# Rule-based Named-Entity-Recognition (NER) Program
**Results:** We reached an accuracy of 75% in extracting vendors' names from transaction memos.

**Methods:**
Our rule-based NER program takes in a list of transaction memos as input and provides a list of vendor names (or indicated failures) as output. The program consists of two parts – cleaning and extraction. In the cleaning process, we remove irrelevant information such as credit card numbers from each memo to ease the extraction of names and locations. Next, in the extraction process, we identify the vendor’s information from the “cleaned” memo. For both cleaning and extraction processes, we recognize the irrelevant information such as dates and transaction reference numbers and identify the patterns of occurrences of vendors’ names and locations for extraction (Chiticariu, Krishnamurthy, Li, Reiss, & Vaithyanathan, 2010). 

![Explanation of Rule-based NER Process]()
Explanation of the rule-based NER process and what happens in each stage from inputting the disorganized sample memo to outputting the name and location of the vendor. 

In the cleaning process, we first removed financial terms, such as “credit card” and “debit card,” dates, transaction reference numbers, credit card numbers, and phone numbers so the memos only contain the names and the locations. The patterns that pointed to these irrelevant words are mixed alphanumerics, a word with more than 5 consecutive digits and punctuations such as hyphens, and the shorthands for financial terms such as “Crd”. Then we checked whether the extraction of vendors’ names was possible. If the memo string only has 3 characters or less, or that the memo string contains the words such as “Mr.” which suggests personal transfer, we removed the memo from the list because the memo did not have organization names that are longer than 3 characters for extraction.

Next, we passed the clean list through the following extraction functions:
1. If words are repeated, return them as the name.
2. If words are between quotation marks, return them as the name.
3. Return words before company suffixes such as “Inc” as the name
4. Return the entire memo as name if the word count in the memo is fewer than 3.
If none of the extraction patterns is successful, the program outputs nothing and lets the user know that the program has failed to extract a vendor name from the memo.
