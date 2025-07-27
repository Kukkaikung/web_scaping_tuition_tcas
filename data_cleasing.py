import pandas as pd
import re

# โหลดไฟล์ CSV
df = pd.read_csv("tcas_programs.csv")

# ดึงเฉพาะบางคอลัมน์
selected_columns = ['มหาวิทยาลัย', 'ค่าใช้จ่าย', 'ชื่อหลักสูตร', 'ชื่อหลักสูตรภาษาอังกฤษ']
new_df = df[selected_columns].copy()

# ใช้ regex เพื่อดึงเฉพาะตัวเลขแรกที่อยู่หน้าคำว่า "บาท" หรือ "/เทอม"
# เช่น "ประมาณ 18,000 บาท/เทอม" จะได้ 18000
# จะดึงเฉพาะเลขหลักแรกที่เจอ และแปลงให้เป็นเลข (int)

new_df['ค่าใช้จ่าย'] = new_df['ค่าใช้จ่าย'].str.replace(',', '')  # ลบ comma ออกจากตัวเลข
new_df['ค่าใช้จ่าย'] = new_df['ค่าใช้จ่าย'].str.extract(r'(\d+)(?=\s*บาท|\s*/เทอม|\s*/ภาคเรียน)')  # ดึงตัวเลขก่อน "บาท", "/เทอม", "/ภาคเรียน"
new_df['ค่าใช้จ่าย'] = pd.to_numeric(new_df['ค่าใช้จ่าย'], errors='coerce')  # แปลงเป็นตัวเลข (NaN ถ้าไม่เจอ)

# บันทึกไฟล์ใหม่
new_df.to_csv("filtered_tcas_cleaned.csv", index=False, encoding='utf-8-sig')

print("บันทึกไฟล์ filtered_tcas_cleaned.csv เรียบร้อยแล้ว")
