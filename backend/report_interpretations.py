"""Canonical AstroSage-style interpretation paragraphs for each Ashtakoota guna.
Verbatim paragraphs derived from professional Vedic horoscope-matching references.
Keyed by (boy_value, girl_value). Falls back to score-tier text when key is missing.
"""

# Tara name by count - 9 cycle: Janma, Sampat, Vipat, Kshema, Pratyak, Sadhana, Vadha, Mitra, Maha-Mitra
TARA_NAMES = ["Janam", "Sampat", "Vipat", "Kshema", "Pratyak", "Sadhana", "Vadha", "Mitra", "Maha-Mitra"]


def tara_name(count: int) -> str:
    r = count % 9
    if r == 0:
        r = 9
    return TARA_NAMES[r - 1]


# ---------- VARNA ----------
VARNA_INTERP = {
    ("Vaishya", "Vaishya"): "The boy and the girl both belong to Vaishya varan. This combination indicates a sensitive, psychic and emotional understanding between the natives. The boy would be able to sort out domestic tribulations nicely and the girl will look after the house nicely. Together their energy flows from a positive to a negative terminal, just like a battery, which brings out best results. Both are loyal, sympathetic and attractive towards each other. In their lives, flow of life force is harmonious. Overall, it's a nice merge.",
    ("Brahmin", "Brahmin"): "Both the boy and the girl belong to Brahmin varan. They are equally evolved spiritually and intellectually. Their bond is rooted in shared wisdom, devotion to dharma and a calm, contemplative life together. Overall, this is a deeply harmonious merge.",
    ("Kshatriya", "Kshatriya"): "Both belong to Kshatriya varan. They are bold, courageous and ambitious in equal measure. While their drive complements each other, they must guard against ego clashes. Properly channelled, their union becomes a force of action and protection.",
    ("Shudra", "Shudra"): "Both belong to Shudra varan. They share a grounded, service-oriented disposition and find joy in life's simple, tangible pleasures. The compatibility on the work and devotion plane is strong.",
}
VARNA_FALLBACK = {
    "good": "The boy's varan is higher than or equal to the girl's. This combination is considered favourable by sages — it indicates that the masculine spiritual energy will provide stability, while the feminine energy nourishes the home. Their wavelengths complement each other and the union is auspicious.",
    "bad": "The boy's varan is lower than the girl's. Traditionally this is considered less favourable because the natural flow of spiritual authority is reversed. With conscious effort, mutual respect and shared purpose this can still be overcome.",
}


# ---------- VASHYA ----------
VASHYA_INTERP = {
    ("Chatushpada", "Chatushpada"): "The boy and the girl both come under Chatushpad vashya. This pair indicates capability of achieving happiness, health and status together. There is good aspect of decent married life as both have a fair demand on each other on certain occasions. They encourage each other and mutual responsibility makes them loyal and attractive for each other. This combination comes out effectively in work and study and in matters related to diet, dress and personal hygiene. Both will have an emotional and a very soft-core for each other in their hearts.",
    ("Manav", "Manav"): "Both belong to Manav (human) vashya. They have a deeply civilised, cooperative and intellectual approach to relationships. Their interaction is mature, communicative and respectful. The marriage promises a stable, dignified domestic life.",
    ("Jalachar", "Jalachar"): "Both belong to Jalachar (water-dwelling) vashya. They share emotional depth and intuition. Their bond is fluid, adaptable and deeply caring. Overall a very compatible energetic match.",
}
VASHYA_FALLBACK = {
    "good": "Their vashya groups complement one another. There is mutual influence and gentle dominance flowing in both directions. Day-to-day cooperation in worldly matters is harmonious.",
    "neutral": "Their vashya groups are different but not antagonistic. Some adjustment is needed in dominance and expectation but the relationship remains workable.",
    "bad": "Their vashya groups belong to opposing categories. There may be conscious or unconscious tussles for dominance. With awareness and patience this can be navigated.",
}


# ---------- TARA ----------
TARA_INTERP = {
    ("Vipat", "Janam"): "Tara for boy is Vipat while the girl belongs to Janam tara. The relationship allows for imperfection and limitations of both people involved. Compatibility chart of the boy and the girl indicate growth of family might be hindered or delayed. Difference of opinion may also lead towards personality clashes. The boy can rise above pettiness and jealousy, if they learn to share the good with the bad. Through mutual understanding they can get over any adverse situation. However, if other gunas are matched well, then this match may be taken into consideration.",
}
TARA_FALLBACK = {
    "good": "The taras of the boy and the girl form an auspicious combination. This indicates good health, prosperity and steady growth of family. The relationship is blessed by the natural cosmic rhythm and faces fewer obstacles.",
    "mixed": "The taras of the boy and the girl form a partially favourable combination. Some areas of life will flow smoothly while others may demand patience. Mutual support balances the unevenness.",
    "bad": "The taras form a less favourable combination. There may be intermittent challenges to health, progeny or family expansion. Through mutual understanding and shared faith, the natives can overcome these adversities, especially if other gunas score well.",
}


# ---------- YONI ----------
YONI_INTERP = {
    ("Mesh", "Vanar"): "Yoni for boy is Mesh while for girl is Vanar. Both are animals of different mental and emotional plane. The boy behaves indifferent at sometimes. The girl will think boy as impractical and lack of financial sense. He will be friendly and social and would love to spend time outside home. On the other hand, she will be introvert and like spending time at home alone. They will find it difficult to understand each other's mood and feelings. There will be basic differences in the way the approach the life. Physically, this is not a satisfactory union.",
    ("Horse", "Horse"): "Both share the Horse yoni. Their physical, emotional and mental impulses are perfectly aligned. The union is passionate, energetic and deeply satisfying.",
}
YONI_FALLBACK = {
    "same": "Both partners share the same yoni. Their physical, emotional and instinctive natures are aligned. This is regarded as one of the strongest indications of a happy, satisfying union.",
    "friendly": "Their yonis belong to friendly animal categories. There is natural attraction and easy understanding on the physical and emotional plane. The marriage promises affection and harmony.",
    "neutral": "Their yonis are neutral towards each other. There is neither strong attraction nor strong repulsion — sustained intimacy will require gentle effort and emotional openness.",
    "enemy": "Their yonis belong to opposing animal categories which are traditionally regarded as enemies. There may be fundamental differences in instincts, moods and physical expression. Conscious adjustment will be required.",
}


# ---------- MAITRI (Graha Maitri) ----------
MAITRI_INTERP = {
    ("Venus", "Saturn"): "The boy belongs to the rasi lord Venus and the girl belongs to Saturn's lordship. As the compatibility chart shows it is an excellent combination. They show their full love, affection, desire, support, assurance, comfort, encouragement and protection to each other. Your emotional ties create a better understanding of each other that will draw you closer together and keep you there over the long haul. Success in relationships comes easily to them. There will be a sense of mutual respect and just dealing. Overall, the relationship will be joyous and rewarding.",
}
MAITRI_FALLBACK = {
    "same": "Both partners share the same rasi lord. Their psychological wavelengths are perfectly attuned. They understand each other almost without words. The union promises deep, lasting friendship.",
    "friendly": "The rasi lords of the boy and the girl are friendly to each other. They display love, affection, support and protection naturally. Emotional bonds form easily and last long. The union is joyous and rewarding.",
    "neutral": "The rasi lords are neutral. The relationship will be civil and respectful but may require effort to ignite deeper emotional warmth. Shared experiences gradually build the bond.",
    "enemy": "The rasi lords of the boy and the girl are enemies in the traditional planetary scheme. There may be subconscious distrust and difficulty understanding each other's psychological motives. Conscious work on empathy is essential.",
}


# ---------- GANA ----------
GANA_INTERP = {
    ("Rakshasa", "Deva"): "The boy belongs to Rakshasha gan and the girl belongs to Dev gan. As the name suggests, this combination is not regarded good by sages. This relationship characterize by aggression and lack of understanding. Generally such relationships are insincere and lacks the trust and confidence required. Their nature and philosophy will contradict each other. The boy will think that the girl is greedy, demanding and sometimes unethical. The girl will think that the boy is lazy and lacks the practical know-how required to deal worldly matters. There will be a lack of understaning which will lead to domestic disputes. This combination produces clashes and quarrels over family and financial matters.",
    ("Deva", "Deva"): "Both the boy and the girl belong to Dev gan. They share a noble, gentle and idealistic disposition. They believe in dharma, peace and harmony in family life. The marriage promises serenity and mutual upliftment.",
    ("Manushya", "Manushya"): "Both belong to Manushya gan. They are humane, balanced and worldly-wise. They negotiate life with maturity and a sense of fairness. The union is steady, prosperous and well respected.",
    ("Rakshasa", "Rakshasa"): "Both belong to Rakshasa gan. They are passionate, intense and fiercely loyal. The chemistry is strong but tempers run high — channelled positively, the union has great power.",
}
GANA_FALLBACK = {
    "compatible": "The gans of both partners are reasonably compatible. Differences in temperament exist but are bridged by mutual respect and shared purpose.",
    "incompatible": "The gans of both partners are traditionally incompatible. Their fundamental temperaments and value systems differ, which can cause friction. Conscious cultivation of empathy is recommended.",
}


# ---------- BHAKOOT ----------
BHAKOOT_INTERP = {
    ("Vrishabha", "Makara"): "Vrishabha sign is for boy and the girl belongs to Makar sign. This is not a good sign match. She will be practical, traditional and down-to-earth. He will be fashionable, flamboyant and showman. She will be unpredictable and moody which will not go well with him. He is crafty and and she will be slow in responding to his actions. This is also regarded a detrimental combination for progeny, so this match should be avoided, if possible.",
}
BHAKOOT_FALLBACK = {
    "good": "The Bhakoot combination of the boy and the girl is auspicious. It promises domestic happiness, financial prosperity and harmonious progeny. The marriage is blessed in matters of wealth and family welfare.",
    "neutral": "The Bhakoot combination is neutral. The marriage will be steady but will require deliberate cultivation of common goals.",
    "bad": "The Bhakoot combination is regarded as inauspicious by sages. It can affect family welfare, finances or progeny. With wisdom, mutual respect and remedial measures from a learned astrologer, the difficulty can be mitigated.",
}


# ---------- NADI ----------
NADI_INTERP = {
    ("Antya", "Antya"): "The boy and the girl, both belong to Antya nadi. It is not a good sign from the viewpoint of compatibility. It has the negative effect on the longevity of marriage. They will not get along well and feel a lot of difference in their ways of thinking. They will not be able to understand moods of each other and it will be very difficult for them to adjust according to one another. They may face several problems due to continuous ego clashes.",
    ("Aadi", "Aadi"): "Both belong to Aadi nadi. Same-nadi combinations are traditionally considered unfavourable for health and progeny. Remedial measures are recommended.",
    ("Madhya", "Madhya"): "Both belong to Madhya nadi. Same-nadi combinations are considered unfavourable for health and progeny. Consultation with a learned astrologer for remedial measures is advised.",
}
NADI_FALLBACK = {
    "good": "The boy and the girl belong to different nadis. This is the most auspicious of indicators in Vedic matchmaking. It promises strong genetic compatibility, healthy progeny and longevity of marriage.",
    "bad": "The boy and the girl belong to the same nadi. Same-nadi matches are traditionally considered the most serious of doshas, with implications for health and progeny. Consultation with a learned astrologer for remedial measures is highly recommended.",
}


def interpret(guna: str, boy: str, girl: str, score: int, max_pts: int) -> str:
    """Return AstroSage-style interpretation paragraph."""
    pct = score / max_pts if max_pts else 0
    if guna == "Varna":
        if (boy, girl) in VARNA_INTERP:
            return VARNA_INTERP[(boy, girl)]
        return VARNA_FALLBACK["good"] if score >= 1 else VARNA_FALLBACK["bad"]
    if guna == "Vashya":
        if (boy, girl) in VASHYA_INTERP:
            return VASHYA_INTERP[(boy, girl)]
        if score == max_pts:
            return VASHYA_FALLBACK["good"]
        return VASHYA_FALLBACK["neutral"] if score > 0 else VASHYA_FALLBACK["bad"]
    if guna == "Tara":
        if (boy, girl) in TARA_INTERP:
            return TARA_INTERP[(boy, girl)]
        if pct >= 0.66:
            return TARA_FALLBACK["good"]
        return TARA_FALLBACK["mixed"] if pct >= 0.33 else TARA_FALLBACK["bad"]
    if guna == "Yoni":
        if (boy, girl) in YONI_INTERP:
            return YONI_INTERP[(boy, girl)]
        if boy == girl:
            return YONI_FALLBACK["same"]
        if score >= 3:
            return YONI_FALLBACK["friendly"]
        if score >= 1:
            return YONI_FALLBACK["neutral"]
        return YONI_FALLBACK["enemy"]
    if guna == "Graha Maitri":
        if (boy, girl) in MAITRI_INTERP:
            return MAITRI_INTERP[(boy, girl)]
        if boy == girl:
            return MAITRI_FALLBACK["same"]
        if score >= 4:
            return MAITRI_FALLBACK["friendly"]
        if score >= 2:
            return MAITRI_FALLBACK["neutral"]
        return MAITRI_FALLBACK["enemy"]
    if guna == "Gana":
        if (boy, girl) in GANA_INTERP:
            return GANA_INTERP[(boy, girl)]
        return GANA_FALLBACK["compatible"] if score >= 5 else GANA_FALLBACK["incompatible"]
    if guna == "Bhakoot":
        if (boy, girl) in BHAKOOT_INTERP:
            return BHAKOOT_INTERP[(boy, girl)]
        if score == max_pts:
            return BHAKOOT_FALLBACK["good"]
        return BHAKOOT_FALLBACK["neutral"] if score > 0 else BHAKOOT_FALLBACK["bad"]
    if guna == "Nadi":
        if (boy, girl) in NADI_INTERP:
            return NADI_INTERP[(boy, girl)]
        return NADI_FALLBACK["good"] if score == max_pts else NADI_FALLBACK["bad"]
    return ""


GUNA_AREA = {
    "Varna": "Work", "Vashya": "Dominance", "Tara": "Destiny", "Yoni": "Mentality",
    "Graha Maitri": "Compatibility", "Gana": "Guna Level", "Bhakoot": "Love", "Nadi": "Health",
}


def conclusion(score: float, max_total: int, mangal_a: bool, mangal_b: bool) -> str:
    """Return AstroSage-style verdict line."""
    cancels = mangal_a and mangal_b
    one_has = (mangal_a != mangal_b)
    if score >= 18 and not (one_has and not cancels):
        if score >= 28:
            return "This is an excellent match. The high number of points obtained and absence of any major dosha strongly favour this marriage."
        return "This match is preferable. The match points obtained are within the auspicious range."
    if score < 18 and one_has and not cancels:
        return "This marriage is NOT preferable due to Mangal Dosha and low match points obtained."
    if score < 18:
        return "This marriage is NOT preferable due to low match points obtained."
    return "This marriage requires careful consideration. Mangal Dosha is present in one partner; remedies may be advised before proceeding."


def mangal_statement(name_a: str, name_b: str, mangal_a: bool, mangal_b: bool) -> str:
    a = "Low Mangal Dosha" if mangal_a else "No Mangal Dosha"
    b = "Low Mangal Dosha" if mangal_b else "No Mangal Dosha"
    return f"Mr. {name_a} has '{a}' and Ms. {name_b} has '{b}'."
