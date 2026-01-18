# Handling charges without tax
total_taxable_amt = 11.43
total_c_gst_amt = 0
total_gross_amt = 0
total_discount_amt = 0
total_final_amt = 0

details = [
    {
        "name": "Biodens",
        "price": 223.06,
        "discount": 1.03,
        "qty": 12
    }
]

for detail in details:
    detail["amt"] = (detail["price"] * detail["qty"]) - detail["discount"]
    detail["t_amt"] = f"{detail['amt']:.2f}"
    detail["d_amt"] = f"{detail['discount']:.2f}"
    detail["g_amt"] = f"{detail['amt'] * 0.05:.2f}"
    detail["total_amt"] = f"{detail['amt'] + (detail['amt'] * 0.05):.2f}"

    print(f"{detail["name"]} \t {detail['qty']} \t {detail['d_amt']} \t "
          f"{detail['amt']:.2f} \t "
          f"{detail['g_amt']} \t {detail['total_amt']} \t ")

    total_taxable_amt += float(detail["amt"])
    total_gross_amt += float(detail["g_amt"])+(detail["price"]*detail["qty"])
    total_discount_amt += float(detail["d_amt"])
    total_c_gst_amt += (float(detail["g_amt"]) / 2)
    total_final_amt += float(detail["g_amt"])+detail["amt"]

print()
print("Taxes")
print(f"{total_taxable_amt:.2f} \t {total_c_gst_amt:.2f} \t {total_c_gst_amt:.2f}")
print()
print(f"Total Gross Amount : {total_gross_amt:.2f}")
print(f"Total Handling Charges : {12:.2f}")
print(f"Total Discount Amount : {total_discount_amt:.2f}")
# +12 for total handling charges
print(f"Final Amt : {total_final_amt + 12:.2f}")
