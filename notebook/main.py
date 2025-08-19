import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date
from ged4py.parser import GedcomReader
from ged4py.date import DateValue, DateValueSimple


def parse_date(date_val):
    if pd.isna(date_val):
        return None
    
    # Si c'est un objet DateValue de ged4py
    dict_months = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY":5, "JUN":6, "JUL":7, "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}
    try:
        date_parsed = datetime.combine(date(date_val.date.year, dict_months[date_val.date.month], date_val.date.day), datetime.min.time())
    except:
        date_parsed = datetime(date_val.date.year)
    return date_parsed


gedcom_file = "data/dummy_family.ged"

people = []
with GedcomReader(gedcom_file) as parser:
    for indi in parser.records0("INDI"):  # INDI = individu
        name = indi.name.format()
        gender = indi.sex
        birth_date = indi.sub_tag_value("BIRT/DATE")
        birth_place = indi.sub_tag_value("BIRT/PLAC")
        death_date = indi.sub_tag_value("DEAT/DATE")
        death_place = indi.sub_tag_value("DEAT/PLAC")

        people.append({
            "Name": name,
            "Gender": gender,
            "Birth Date": birth_date,
            "Birth Place": birth_place,
            "Death Date": death_date,
            "Death Place": death_place
        })

df = pd.DataFrame(people)


df["Birth Date"] = df["Birth Date"].apply(parse_date)
df["Death Date"] = df["Death Date"].apply(parse_date)


df["Birth Year"] = df["Birth Date"].apply(lambda d: d.year if d else None)
df["Age at death"] = df.apply(lambda row: (row["Death Date"].year - row["Birth Date"].year) if row["Death Date"] and row["Birth Date"] else None, axis=1)



sns.countplot(x="Gender", data=df)
plt.title("Gender distribution")
plt.savefig("plots/gender.png")
plt.close()


sns.histplot(df["Birth Year"].dropna(), bins=30, kde=False)
plt.title("Distribution by birth year")
plt.xlabel("Birth year")
plt.ylabel("Number of individuals")
plt.savefig("plots/birthyear.png")
plt.close()



df["Century"] = (df["Birth Year"] // 100 + 1).astype("Int64")
life_by_century = df.groupby("Century")["Age at Death"].mean()

life_by_century.plot(kind="bar")
plt.title("Avg age at death by birth century")
plt.ylabel("Avg age")
plt.savefig("plots/avg_age.png")
plt.close()