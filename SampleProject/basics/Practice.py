d = 131.5
dd = 109.38 -25
dn = 6
mn = 7
m = 139.69
md = 33.07-6

print("D")
dta = (dn * d) - dd
print(f"Taxable Amt : {dta:.2f}")
print(f"Discount Amt : {dd:.2f}")
print(f"GST Amt : {(dta * 0.05):.2f}")
print(f"Total Amt : {(dta * 0.05) + dta:.2f}")

print("M")
mta = (mn * m) - md
print(f"Taxable Amt : {mta:.2f}")
print(f"Discount Amt : {md:.2f}")
print(f"GST Amt : {(mta * 0.05):.2f}")
print(f"Total Amt : {(mta * 0.05) + mta:.2f}")

print()
print(f"Total Taxable Amt : {(dta+mta+11.43):.2f}")
print(f"Total CGST : {((dta * 0.05)+(mta * 0.05))/2:.2f}")
print()
print(f"Total Gross Amount : {((dn * d)+(mn * m)+(mta * 0.05)+(dta * 0.05)):.2f}")
print(f"Total Handling Charges : {12:.2f}")
print(f"Total Discount Amount : {(dd + md):.2f}")
print(f"Final Amt : {(mta * 0.05) + mta + (dta * 0.05) + dta + 12:.2f}")
