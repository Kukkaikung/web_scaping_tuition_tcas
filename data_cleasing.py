import pandas as pd

# โหลดไฟล์ CSV
df = pd.read_csv("tcas_programs.csv")

# ดึงเฉพาะบางคอลัมน์
selected_columns = ['มหาวิทยาลัย', 'ค่าใช้จ่าย', 'ชื่อหลักสูตร', 'ชื่อหลักสูตรภาษาอังกฤษ']
new_df = df[selected_columns].copy()

# ลบ , ออกจากตัวเลข
new_df['ค่าใช้จ่าย'] = new_df['ค่าใช้จ่าย'].str.replace(',', '')

# ดึงตัวเลขก่อนคำว่า "บาท", "/เทอม", "/ภาคเรียน"
new_df['ค่าใช้จ่าย'] = new_df['ค่าใช้จ่าย'].str.extract(r'(\d+)(?=\s*บาท|\s*/เทอม|\s*/ภาคเรียน)')
new_df['ค่าใช้จ่าย'] = pd.to_numeric(new_df['ค่าใช้จ่าย'], errors='coerce')

# หากค่าใช้จ่าย > 100000 ให้หาร 8
new_df.loc[new_df['ค่าใช้จ่าย'] > 100000, 'ค่าใช้จ่าย'] = new_df['ค่าใช้จ่าย'] / 8

# 🔢 แปลงค่าใช้จ่ายให้เป็น int (ปัดเศษก่อนถ้าต้องการ)
new_df['ค่าใช้จ่าย'] = new_df['ค่าใช้จ่าย'].round().astype('Int64')  # ใช้ Int64 รองรับ NaN ด้วย

# บันทึกไฟล์ใหม่
new_df.to_csv("filtered_tcas_cleaned.csv", index=False, encoding='utf-8-sig')

print("บันทึกไฟล์ filtered_tcas_cleaned.csv เรียบร้อยแล้ว")
