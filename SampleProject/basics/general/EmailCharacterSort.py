"""
EmailSort

Question:
First get all the alphabets of the email then sort the alphabets then without changing the
position of the special characters and numbers just replace alphabets

Examples

Input: pencil@gmail.com
Output : accegi@illmm.nop

Input : hi.hello@gmail.com
Output : ac.eghhi@illlm.moo

Topics : Regex, join()
"""

import re


def email_character_sort(email):
    regex = r'[A-Za-z]'
    email_chars = list(email)
    characters=list()
    characters_pos=list()

    for i in range (len(email_chars)):
        matcher=re.fullmatch(regex,email_chars[i])
        if matcher:
            characters.append(email_chars[i])
            characters_pos.append(i)

    characters=sorted(characters)

    for i in range (len(characters)):
        email_chars[characters_pos[i]]=characters[i]

    return ''.join(email_chars)


if __name__ == "__main__":
    print("pencil@gmail.com : "+email_character_sort("pencil@gmail.com"))
    print("hi.hello@gmail.com : "+email_character_sort("hi.hello@gmail.com"))
