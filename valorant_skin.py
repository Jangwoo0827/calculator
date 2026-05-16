import streamlit as st
import requests

# 1. API 데이터 호출 함수
@st.cache_data
def get_val_data(endpoint):
    try:
        url = f"https://valorant-api.com/v1/{endpoint}"
        res = requests.get(url, params={"language": "ko-KR"})
        return res.json()['data']
    except:
        return []

st.set_page_config(page_title="발로란트 스킨", layout="wide")

# 데이터 로드
all_weapons = get_val_data("weapons")
all_skins = get_val_data("weapons/skins")
all_tiers = get_val_data("contenttiers")

# 2. 사이드바 필터 구성
st.sidebar.header("🔍 커스텀 필터")

# (1) 이름 검색
search_query = st.sidebar.text_input("스킨/세트 이름 검색", placeholder="예: 약탈자, RGX")

# (2) 총기 종류 선택
weapon_names = ["전체", "근접 무기"] + [w['displayName'] for w in all_weapons if w['displayName'] != "근접 무기"]
selected_weapon = st.sidebar.selectbox("총기 종류", weapon_names)

# (3) 등급 필터 (아이콘 포함)
tier_dict = {t['displayName']: t['uuid'] for t in all_tiers}
tier_names = ["전체"] + list(tier_dict.keys())
selected_tier_name = st.sidebar.selectbox("스킨 등급", tier_names)

# 3. 강화된 필터링 로직
def get_filtered_list():
    items = [s for s in all_skins if s.get('displayIcon') and "Standard" not in s['displayName']]
    
    # 총기 필터
    if selected_weapon == "근접 무기":
        items = [s for s in items if "근접" in s['displayName'] or "Melee" in s.get('assetPath', '')]
    elif selected_weapon != "전체":
        items = [s for s in items if selected_weapon in s['displayName']]
    
    # 등급 필터
    if selected_tier_name != "전체":
        target_tier_uuid = tier_dict.get(selected_tier_name)
        items = [s for s in items if s.get('contentTierUuid') == target_tier_uuid]
    
    # 검색어 필터
    if search_query:
        items = [s for s in items if search_query.lower() in s['displayName'].lower()]
        
    return items

final_list = get_filtered_list()

# 4. 페이지네이션
items_per_page = 8
total_pages = max((len(final_list) // items_per_page) + (1 if len(final_list) % items_per_page > 0 else 0), 1)
page = st.sidebar.number_input("페이지", min_value=1, max_value=total_pages, step=1)

start_idx = (page - 1) * items_per_page
display_items = final_list[start_idx : start_idx + items_per_page]

# 5. 메인 화면 출력
# 선택된 등급의 아이콘이 있다면 타이틀 옆에 표시
tier_icon_html = ""
if selected_tier_name != "전체":
    icon_url = next(t['displayIcon'] for t in all_tiers if t['displayName'] == selected_tier_name)
    st.image(icon_url, width=50)

st.title(f"발로란트 스킨")
st.info(f"결과: {len(final_list)}개 | 필터: {selected_weapon} / {selected_tier_name}")

if not display_items:
    st.warning("일치하는 스킨이 없습니다. 필터를 조정해 보세요!")
else:
    cols = st.columns(2)
    for idx, skin in enumerate(display_items):
        with cols[idx % 2]:
            with st.container(border=True):
                # 스킨 이름 및 등급 아이콘 소형 표시
                st.subheader(skin['displayName'])
                
                tab1, tab2 = st.tabs(["🎨 외형/크로마", "🎬 영상/킬소리"])
                
                with tab1:
                    chromas = [c for c in skin.get('chromas', []) if c.get('fullRender') or c.get('displayIcon')]
                    if len(chromas) > 1:
                        c_names = [c['displayName'] for c in chromas]
                        sel_c = st.selectbox("버전 선택", c_names, key=f"c_{skin['uuid']}_{idx}")
                        target = next(c for c in chromas if c['displayName'] == sel_c)
                        st.image(target.get('fullRender') or target.get('displayIcon'), use_container_width=True)
                    else:
                        st.image(skin['displayIcon'], use_container_width=True)
                
                with tab2:
                    vids = [l for l in skin.get('levels', []) if l.get('streamedVideo')]
                    if vids:
                        for v in vids:
                            st.caption(f"📌 {v['displayName']}")
                            st.video(v['streamedVideo'])
                    else:
                        st.write("특수 효과 영상이 없는 스킨입니다.")