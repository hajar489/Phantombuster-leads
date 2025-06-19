#!/usr/bin/env python
# coding: utf-8

# In[51]:


import pandas as pd
import os

# Zorg dat de output map bestaat
os.makedirs("Phantombuster_leads", exist_ok=True)

def extract_post_links(posts_url):
    if pd.isna(posts_url):
        return []
    return [link.strip() for link in posts_url.split('|') if link.strip()]

# 1. Laad de nieuwe maanddata
df1 = pd.read_csv("datasets/Phantombuster_Dataset_1.csv")
df2 = pd.read_csv("datasets/Phantombuster_Dataset_2.csv")
df3 = pd.read_csv("datasets/Phantombuster_Dataset_3.csv")
df4 = pd.read_csv("datasets/Phantombuster_Dataset_4.csv")
df_new = pd.concat([df1, df2, df3, df4], ignore_index=True)
df_new["Posts Url"] = df_new["Posts Url"].apply(extract_post_links)

# 2. Groepeer nieuwe data per profiel
df_new_grouped = df_new.groupby("Profile Link").agg({
    "Full Name": "first",
    "First Name": "first",
    "Last Name": "first",
    "Posts Url": lambda x: sum(x, [])
}).reset_index()

df_new_grouped["Posts Url"] = df_new_grouped["Posts Url"].apply(lambda x: list(set(x)))
df_new_grouped["Aantal likes nieuw"] = df_new_grouped["Posts Url"].apply(len)

# 3. Laad de vorige maand (indien beschikbaar)
if os.path.exists("Historisch_Likes_Dataset__Vorige_Maand_ (1).csv"):
    df_old = pd.read_csv("Historisch_Likes_Dataset__Vorige_Maand_ (1).csv")
    df_old["Posts Url"] = df_old["Posts Url"].apply(lambda x: extract_post_links(x))
else:
    df_old = pd.DataFrame(columns=df_new_grouped.columns.tolist() + ["Aantal likes totaal"])
    df_old["Posts Url"] = df_old["Posts Url"].astype(object)

# 4. Merge vorige en nieuwe data
df_merged = pd.merge(df_old, df_new_grouped, on="Profile Link", how="outer", suffixes=("_oud", "_nieuw"))

def merge_posts(old_posts, new_posts):
    if isinstance(old_posts, list) and isinstance(new_posts, list):
        return list(set(old_posts + new_posts))
    elif isinstance(new_posts, list):
        return new_posts
    elif isinstance(old_posts, list):
        return old_posts
    else:
        return []

df_merged["Alle posts cumulatief"] = df_merged.apply(lambda row: merge_posts(row.get("Posts Url_oud"), row.get("Posts Url_nieuw")), axis=1)
df_merged["Aantal likes totaal"] = df_merged["Alle posts cumulatief"].apply(lambda x: len(set(x)))

# 5. Output formatteren
output = pd.DataFrame({
    "Profile Link": df_merged["Profile Link"],
    "Full Name": df_merged["Full Name_nieuw"].combine_first(df_merged["Full Name_oud"]),
    "First Name": df_merged["First Name_nieuw"].combine_first(df_merged["First Name_oud"]),
    "Last Name": df_merged["Last Name_nieuw"].combine_first(df_merged["Last Name_oud"]),
    "Posts Url": df_merged["Alle posts cumulatief"].apply(lambda x: " | ".join(x)),
    "Aantal likes totaal": df_merged["Aantal likes totaal"]
})

from datetime import datetime

# Genereer de datum als string
vandaag = datetime.today().strftime("%Y-%m-%d")

# Sla het bestand op met datum in de naam
output_path = f"output/likes_per_profiel_{vandaag}.csv"
output.to_csv(output_path, index=False)


# In[ ]:




