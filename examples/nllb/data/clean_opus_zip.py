import re
import zipfile


def replace_func(m):
    return m.group(1)


def clean_zip_from_url_xml_tags(z_in_path, z_out_path, lang_code):
    with zipfile.ZipFile(z_in_path, "r") as zip_file_read:
        z_files_info = zip_file_read.infolist()
        z_files = [el.filename for el in z_files_info]
        print(z_files_info)
        print(z_files)

    for i, zip_file_info in enumerate(z_files_info):
        print(f'{i}/{len(z_files)}')
        # Use glob to fine *.xml files:
        if zip_file_info.filename.endswith(".xml"):
            with zipfile.ZipFile(z_in_path, "r") as zip_file_read:
                with zip_file_read.open(zip_file_info.filename) as myfile:
                    f1_txt = myfile.read()
                    try:
                        f1_txt = f1_txt.decode("utf-8", "replace")  # Step 1: fix encoding issues.
                    except Exception as e:
                        print(zip_file_info.filename, e)
                        continue
            # Step 2: replace the <URL/> with URL.
            matches = re.findall(r'<(http[^>]*)\/>', f1_txt)
            if (matches):
                f1_txt = re.sub(r'<(http[^>]*)\/>', replace_func, f1_txt)
                matches = re.findall(r'<(http[^>]*)\/>', f1_txt)
                assert len(matches) == 0, "There should be no matches left that have <URL/> pattern."
                matches = re.findall(r'(http[^>]*)', f1_txt)
                assert (len(matches) > 0), "we should not remove the URLs."
            # Step 3: remove <> tags.
            matches = re.findall(r'<>', f1_txt)
            if (matches):
                f1_txt = re.sub(r'<>', "", f1_txt)
                matches = re.findall(r'<>', f1_txt)
                assert len(matches) == 0, "There should be no matches left that have <URL/> pattern."
            # TODO: add more edge cases if we want to get some of these messed up datasets into shape (e.g. Ubuntu, GNOME)

            # Write the file back to the zip:
            with zipfile.ZipFile(z_out_path, "a", zipfile.ZIP_DEFLATED) as zip_file_write:
                zip_file_write.writestr(zip_file_info.filename, f1_txt)


def clean_zip_from_xml_tags():
    # Experimental code, hence leaving the paths hardcoded.
    corpus = "GNOME"
    src_lang_code = "en"
    trg_lang_code = "sr"

    z1_in_path = f"/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/Opus_{trg_lang_code}/opus_download_{trg_lang_code}/{corpus}_latest_raw_{src_lang_code}.zip"
    z1__out_path = f"/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/Opus_{trg_lang_code}/opus_download_{trg_lang_code}/{corpus}_latest_raw_{src_lang_code}_out.zip"
    z2_in_path = f"/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/Opus_{trg_lang_code}/opus_download_{trg_lang_code}/{corpus}_latest_raw_{trg_lang_code}.zip"
    z2_out_path = f"/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/Opus_{trg_lang_code}/opus_download_{trg_lang_code}/{corpus}_latest_raw_{trg_lang_code}_out.zip"

    clean_zip_from_url_xml_tags(z1_in_path, z1__out_path, src_lang_code)
    clean_zip_from_url_xml_tags(z2_in_path, z2_out_path, trg_lang_code)


if __name__ == "__main__":
    clean_zip_from_xml_tags()