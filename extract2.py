import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json

# list of URLs (unchanged)
urls = [
"http://ssgec.ac.in/admin/media_corner/65e2f35c0ab3d5.93305133.bmp",
"https://ssgec.ac.in",
"https://ssgec.ac.in/",
"https://ssgec.ac.in/AboutInstitute.php",
"https://ssgec.ac.in/AffiliationReports.php",
"https://ssgec.ac.in/AlumniAssociation.php",
"https://ssgec.ac.in/AntiRaggingCell.php",
"https://ssgec.ac.in/Canteen.php",
"https://ssgec.ac.in/CellForSpeciallyAbled.php",
"https://ssgec.ac.in/Courses.php",
"https://ssgec.ac.in/CulturalEvents.php",
"https://ssgec.ac.in/DepartmentDetails.php?did=1",
"https://ssgec.ac.in/DepartmentDetails.php?did=2",
"https://ssgec.ac.in/DepartmentDetails.php?did=3",
"https://ssgec.ac.in/DepartmentDetails.php?did=4",
"https://ssgec.ac.in/DepartmentDetails.php?did=5",
"https://ssgec.ac.in/DepartmentDetails.php?did=6",
"https://ssgec.ac.in/DepartmentDetails.php?did=7",
"https://ssgec.ac.in/DepartmentDetails.php?did=8",
"https://ssgec.ac.in/DepartmentDetails.php?did=9",
"https://ssgec.ac.in/DepartmentalNotices.php?did=1",
"https://ssgec.ac.in/DepartmentalNotices.php?did=2",
"https://ssgec.ac.in/DepartmentalNotices.php?did=3",
"https://ssgec.ac.in/DepartmentalNotices.php?did=4",
"https://ssgec.ac.in/DepartmentalNotices.php?did=5",
"https://ssgec.ac.in/DepartmentalNotices.php?did=6",
"https://ssgec.ac.in/DepartmentalNotices.php?did=7",
"https://ssgec.ac.in/DepartmentalNotices.php?did=8",
"https://ssgec.ac.in/DepartmentalNotices.php?did=9",
"https://ssgec.ac.in/EoAs.php",
"https://ssgec.ac.in/Establishment.php",
"https://ssgec.ac.in/EventsOrganized.php",
"https://ssgec.ac.in/Faculties.php",
"https://ssgec.ac.in/FelicitationByIndustries.php",
"https://ssgec.ac.in/FinishingSchool.php",
"https://ssgec.ac.in/GSIRFAndNIRF.php",
"https://ssgec.ac.in/Hostel.php",
"https://ssgec.ac.in/IIIC.php",
"https://ssgec.ac.in/IQAC.php",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=138",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=139",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=140",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=150",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=151",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=155",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=157",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=162",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=163",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=165",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=167",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=174",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=175",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=176",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=177",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=178",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=179",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=183",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=184",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=185",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=186",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=187",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=188",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=193",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=196",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=202",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=212",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=213",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=215",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=216",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=218",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=219",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=220",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=221",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=222",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=224",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=225",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=226",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=227",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=228",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=232",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=238",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=239",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=242",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=243",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=244",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=245",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=247",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=250",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=254",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=257",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=258",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=259",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=260",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=262",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=264",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=266",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=267",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=268",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=269",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=270",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=271",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=272",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=274",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=275",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=287",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=288",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=291",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=295",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=296",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=297",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=298",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=299",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=300",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=304",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=305",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=306",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=307",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=308",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=309",
"https://ssgec.ac.in/IndividualFacultyDetails.php?fid=310",
"https://ssgec.ac.in/Library.php",
"https://ssgec.ac.in/MandatoryDisclosures.php",
"https://ssgec.ac.in/MediaCorner.php",
"https://ssgec.ac.in/NSS.php",
"https://ssgec.ac.in/NewsLetters.php",
"https://ssgec.ac.in/PhotoGallery.php",
"https://ssgec.ac.in/PlacementNews.php",
"https://ssgec.ac.in/Publications.php",
"https://ssgec.ac.in/RUSA.php",
"https://ssgec.ac.in/SSIP.php",
"https://ssgec.ac.in/Scholarship.php",
"https://ssgec.ac.in/SkillEmpowerment.php",
"https://ssgec.ac.in/SportsEvents.php",
"https://ssgec.ac.in/StudentAchievements.php",
"https://ssgec.ac.in/StudentGrievanceRedressalCell.php",
"https://ssgec.ac.in/StudentSection.php",
"https://ssgec.ac.in/TAndP.php",
"https://ssgec.ac.in/TechnicalEvents.php",
"https://ssgec.ac.in/VideoGallery.php",
"https://ssgec.ac.in/Webinars.php",
"https://ssgec.ac.in/WomenDevelopmentCell.php",
"https://ssgec.ac.in/index.php",
"https://www.ssgec.ac.in/alumni/AlumniLogin.php",
"https://www.ssgec.ac.in/alumni/ForgotPassword.php",
"https://www.ssgec.ac.in/alumni/Register.php"
]


def get_page_title(soup, url):
    try:
        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)

        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")
        if path_parts:
            return path_parts[-1].replace("-", " ").replace(".php", "").title()

        if soup.title and soup.title.string:
            return soup.title.string.strip()

        return "Unknown Page"
    except:
        return "Unknown Page"


async def fetch(url, session):
    try:
        async with session.get(url, timeout=15) as response:
            return await response.text()
    except Exception as e:
        print(f"⚠ Failed to fetch {url}: {e}")
        return None


def extract_header_footer(soup):
    try:
        header_footer = []
        header = soup.find("header")
        footer = soup.find("footer")

        if header:
            header_footer.append(header.get_text(separator=" ", strip=True))
        if footer:
            header_footer.append(footer.get_text(separator=" ", strip=True))

        return " ".join([h for h in header_footer if h.strip()])
    except:
        return ""


# 🔥 NEW: Filter noisy text
def is_valid_text(text):
    if not text or len(text.split()) < 5:
        return False

    # Remove menu-like text
    blacklist_keywords = ["home", "contact", "login", "portal"]
    lower_text = text.lower()

    if sum(word in lower_text for word in blacklist_keywords) > 2:
        return False

    return True


async def extract_text_from_webpage(url, session, header_footer_text):
    try:
        html = await fetch(url, session)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        title = get_page_title(soup, url)

        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""

        # Extract paragraphs (filtered)
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if is_valid_text(text):
                paragraphs.append(text)

        # Extract lists (filtered)
        lists = []
        for ul in soup.find_all(["ul", "ol"]):
            items = [li.get_text(strip=True) for li in ul.find_all("li")]
            items = [item for item in items if is_valid_text(item)]
            if items:
                lists.append(" • ".join(items))

        main_text = ". ".join(paragraphs + lists).strip()

        # Remove header/footer
        if header_footer_text:
            main_text = main_text.replace(header_footer_text, "").strip()

        if not main_text:
            main_text = "You may visit the webpage for more information as it might contain tables or images."

        # Extract tables (unchanged)
        tables = []
        for table in soup.find_all("table"):
            table_data = []
            for row in table.find_all("tr"):
                cols = row.find_all(["td", "th"])
                row_data = [col.get_text(strip=True) for col in cols if col.get_text(strip=True)]
                if row_data:
                    table_data.append(row_data)
            if table_data:
                tables.append(table_data)

        return {
            "url": url,
            "title": title,
            "description": description,
            "main_text": main_text,
            "tables": tables
        }

    except Exception as e:
        print(f"⚠ Error processing {url}: {e}")
        return None


async def main():
    try:
        async with aiohttp.ClientSession() as session:
            first_html = await fetch(urls[0], session)
            header_footer_text = ""

            if first_html:
                soup_first = BeautifulSoup(first_html, "html.parser")
                header_footer_text = extract_header_footer(soup_first)

            tasks = [extract_text_from_webpage(url, session, header_footer_text) for url in urls]
            webpage_data = await asyncio.gather(*tasks)

        webpage_data = [data for data in webpage_data if data]

        output = {
            "contact_info": header_footer_text,
            "pages": webpage_data
        }

        with open("college_data.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

        print("✅ Webpage data saved successfully!")

    except Exception as e:
        print(f"⚠ Unexpected error in main(): {e}")


asyncio.run(main())