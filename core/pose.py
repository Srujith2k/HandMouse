# core/pose.py

def is_index_pointing(landmarks) -> bool:
    """
    Simple & effective "pointing" gate:
    - Index finger extended
    - Middle, ring, pinky mostly folded

    Uses y comparisons (works well for typical webcam usage).
    If you point sideways a lot, we can upgrade this to angle-based.
    """

    # Landmark indices (MediaPipe Hands)
    # index: tip=8, pip=6
    # middle: tip=12, pip=10
    # ring: tip=16, pip=14
    # pinky: tip=20, pip=18

    i_tip_y = landmarks[8][1]
    i_pip_y = landmarks[6][1]

    m_tip_y = landmarks[12][1]
    m_pip_y = landmarks[10][1]

    r_tip_y = landmarks[16][1]
    r_pip_y = landmarks[14][1]

    p_tip_y = landmarks[20][1]
    p_pip_y = landmarks[18][1]

    # In image coordinates: smaller y = "higher" (finger extended upward)
    index_extended = i_tip_y < i_pip_y
    middle_folded  = m_tip_y > m_pip_y
    ring_folded    = r_tip_y > r_pip_y
    pinky_folded   = p_tip_y > p_pip_y

    return index_extended and middle_folded and ring_folded and pinky_folded
