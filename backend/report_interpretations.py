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
    ("Brahmin", "Kshatriya"): "The boy is of Brahmin varan and the girl is of Kshatriya varan. The boy's contemplative wisdom complements the girl's courage and drive — a classical pairing of intellect and action. This combination is regarded as auspicious for both worldly success and spiritual progress.",
    ("Brahmin", "Vaishya"): "The boy is of Brahmin varan and the girl is of Vaishya varan. The boy's spiritual orientation tempers the girl's pragmatic energy. Together they balance contemplation with material wisdom, making for a stable and prosperous household.",
    ("Brahmin", "Shudra"): "The boy is of Brahmin varan and the girl is of Shudra varan. The boy's wisdom guides while the girl's grounded service supports. The natural flow of varna is preserved and the union is harmonious in domestic matters.",
    ("Kshatriya", "Vaishya"): "The boy is of Kshatriya varan and the girl is of Vaishya varan. His courage and her practicality form a productive partnership. Material progress comes naturally and the household flourishes.",
    ("Kshatriya", "Shudra"): "The boy is of Kshatriya varan and the girl is of Shudra varan. His leadership is supported by her dedicated service. Roles are clearly defined and the union runs smoothly.",
    ("Vaishya", "Shudra"): "The boy is of Vaishya varan and the girl is of Shudra varan. Together they are a practical, hardworking pair focused on tangible progress and family welfare.",
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
    ("Vanachar", "Vanachar"): "Both belong to Vanachar (forest-dwelling) vashya. They share a wild, independent and nature-aligned disposition. Together they cultivate a free-spirited yet loyal partnership.",
    ("Keet", "Keet"): "Both belong to Keet (insect) vashya. They share an industrious, detail-oriented and persistent temperament. The union is hard-working and resilient.",
    ("Manav", "Chatushpada"): "The boy is of Manav vashya while the girl belongs to Chatushpad vashya. Human and four-legged vashya combine reasonably well — there is mutual attraction and some healthy yielding on both sides. The marriage is workable with affection and care.",
    ("Chatushpada", "Manav"): "The boy is of Chatushpad vashya while the girl belongs to Manav vashya. Chatushpad's loyalty pairs well with Manav's civility. With patience the marriage becomes a fertile, dignified partnership.",
    ("Chatushpada", "Jalachar"): "The boy belongs to Chatushpad vashya while the girl belongs to Jalachar vashya. There is partial compatibility — the four-legged steadiness is softened by water's emotional fluidity. Adjustment is needed but the relationship can blossom.",
    ("Jalachar", "Keet"): "The boy is of Jalachar vashya and the girl is of Keet vashya. The combination is partially compatible — water gives rhythm to the insect's industry. With shared rituals the marriage stabilises.",
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
    ("Elephant", "Elephant"): "Both share the Elephant yoni. The bond is dignified, deeply loyal and carries lifelong devotion. Physical and emotional intimacy unfolds with quiet majesty.",
    ("Cow", "Cow"): "Both belong to the Cow yoni. The union is gentle, nurturing and abundant — a household marked by patience, affection and shared service.",
    ("Tiger", "Tiger"): "Both share the Tiger yoni. Passionate and intense — the union has tremendous magnetism but also requires careful taming of pride and possessiveness.",
    ("Sheep", "Sheep"): "Both share the Sheep yoni. The bond is soft, peaceful and considerate. They find sanctuary in each other's company.",
    ("Serpent", "Serpent"): "Both belong to the Serpent yoni. They share a mysterious, magnetic chemistry. Trust must be cultivated but once formed, it is unshakable.",
    ("Dog", "Dog"): "Both share the Dog yoni. Loyalty is the cornerstone — their love is tireless, protective and home-loving.",
    ("Cat", "Cat"): "Both share the Cat yoni. Independent, sensual and discerning — the union flourishes on mutual respect for each other's space.",
    ("Deer", "Deer"): "Both share the Deer yoni. The bond is graceful, sensitive and refined. Together they cultivate beauty and aesthetic harmony.",
    ("Monkey", "Monkey"): "Both share the Monkey yoni. The relationship is lively, playful and intellectually stimulating. Routine is the only enemy.",
    ("Lion", "Lion"): "Both share the Lion yoni. Two regal souls — the union is bold, prideful and protective. Compromise must be learned but the rewards are vast.",
    ("Buffalo", "Buffalo"): "Both share the Buffalo yoni. Hardworking, steadfast and fertile — the marriage is a deep-rooted partnership built on patience and abundance.",
    ("Mongoose", "Mongoose"): "Both share the Mongoose yoni. Quick-witted, alert and protective — the relationship is energetic and mutually supportive in worldly affairs.",
    ("Rat", "Rat"): "Both share the Rat yoni. The union is industrious, resourceful and family-oriented. Together they accumulate steadily.",
    ("Horse", "Buffalo"): "The boy belongs to Horse yoni and the girl to Buffalo yoni — traditional enemies in the yoni scheme. There can be temperamental clashes, especially around pace and emotional rhythm. Conscious patience is required.",
    ("Cow", "Tiger"): "Cow and Tiger yonis are traditional enemies. Their natural impulses pull in opposite directions; harmony requires deliberate work and respect for each other's instincts.",
    ("Serpent", "Mongoose"): "Serpent and Mongoose yonis are sworn enemies in the traditional scheme. Significant friction is likely; the relationship demands extraordinary effort or remedial measures.",
    ("Cat", "Rat"): "Cat and Rat yonis are predator–prey opposites. Trust will be fragile; the relationship requires a strong foundation of safety and reassurance.",
    ("Dog", "Deer"): "Dog and Deer yonis are traditional enemies. Differing tempers and emotional registers will demand patience.",
    ("Lion", "Elephant"): "Lion and Elephant yonis are regarded as adversarial. Both are powerful and proud — clashes of pride must be carefully navigated.",
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
    ("Sun", "Moon"): "The boy's rasi lord is Sun and the girl's is Moon — the cosmic father and mother. Their bond is archetypal and deeply complementary. He brings will and direction; she brings nourishment and intuition. The union is spiritually significant.",
    ("Mars", "Jupiter"): "The boy's rasi lord is Mars and the girl's is Jupiter — natural friends. His drive is wisely guided by her counsel. The marriage is dynamic, principled and ethically grounded.",
    ("Jupiter", "Mars"): "The boy's rasi lord is Jupiter and the girl's is Mars — natural friends. His wisdom is energised by her dynamism. The relationship is purposeful and full of forward motion.",
    ("Mercury", "Venus"): "The boy's rasi lord is Mercury and the girl's is Venus — friends in the planetary scheme. Communication, beauty and easy companionship characterise this union.",
    ("Saturn", "Venus"): "The boy's rasi lord is Saturn and the girl's is Venus — natural friends. His patience anchors her grace. The bond matures into deep devotion over time.",
    ("Sun", "Mars"): "The boy's rasi lord is Sun and the girl's is Mars — natural friends. Both are fiery and willful; channelled together they accomplish great things, but ego must be tempered.",
    ("Moon", "Sun"): "The boy's rasi lord is Moon and the girl's is Sun. He brings emotional depth, she brings vitality and direction. The union is illuminating and emotionally rich.",
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
    ("Deva", "Manushya"): "The boy is of Dev gan and the girl is of Manushya gan. Their dispositions blend reasonably well — the boy's idealism is grounded by the girl's practicality. The marriage is harmonious in most everyday matters.",
    ("Manushya", "Deva"): "The boy is of Manushya gan and the girl is of Dev gan. The boy's worldliness is uplifted by the girl's gentleness. The bond is workable and pleasing.",
    ("Deva", "Rakshasa"): "The boy is of Dev gan and the girl is of Rakshasa gan — a difficult combination. The boy's gentleness can feel inadequate to the girl's intensity. Friction and misunderstanding are likely; remedies are advised.",
    ("Manushya", "Rakshasa"): "The boy is of Manushya gan and the girl is of Rakshasa gan. The boy's reason struggles against the girl's passion. Their philosophies of life differ; conscious effort is required.",
    ("Rakshasa", "Manushya"): "The boy is of Rakshasa gan and the girl is of Manushya gan. The boy's intensity may overwhelm the girl's measured approach. Adjustment is needed.",
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
    ("Aadi", "Madhya"): "The boy is of Aadi nadi and the girl is of Madhya nadi — different nadis. This is the most auspicious indicator in Vedic matchmaking and points to strong genetic compatibility, healthy progeny and longevity of the union.",
    ("Madhya", "Aadi"): "The boy is of Madhya nadi and the girl is of Aadi nadi — different nadis. The combination is excellent for health, progeny and the longevity of the marriage.",
    ("Aadi", "Antya"): "The boy is of Aadi nadi and the girl is of Antya nadi — different nadis. This is favourable for genetic compatibility and a healthy, long-lasting union.",
    ("Antya", "Aadi"): "The boy is of Antya nadi and the girl is of Aadi nadi — different nadis. Auspicious for progeny and lasting health of the marriage.",
    ("Madhya", "Antya"): "The boy is of Madhya nadi and the girl is of Antya nadi — different nadis. The combination favours health and longevity of the union.",
    ("Antya", "Madhya"): "The boy is of Antya nadi and the girl is of Madhya nadi — different nadis. Auspicious for progeny and union strength.",
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
