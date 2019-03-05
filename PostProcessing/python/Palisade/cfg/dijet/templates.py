"""
module fragment containing some useful functions
"""

from DijetAnalysis.PostProcessing.Palisade.Processors import ContextValue, LiteralString

from .definitions import EXPANSIONS

from matplotlib.font_manager import FontProperties
from matplotlib.colors import SymLogNorm


__all__ = ['FIGURE_TEMPLATES', 'FONTPROPERTIES', 'TEXTS', 'TASK_TEMPLATES']


FONTPROPERTIES = dict(
    big_bold=FontProperties(
        weight='bold',
        family='Nimbus Sans',
        size=20,
    ),
    small_bold=FontProperties(
        weight='bold',
        family='Nimbus Sans',
        size=12,
    ),
    italic=FontProperties(
        style='italic',
        family='Nimbus Sans',
        size=14,
    ),
)

TEXTS = {
    "CMS" : dict(xy=(.05, .9), text=r"CMS", transform='axes', fontproperties=FONTPROPERTIES['big_bold']),
    "PrivateWork" : dict(xy=(.17, .9), text=r"Private Work", transform='axes', fontproperties=FONTPROPERTIES['italic']),
    "AK4PFCHS" : dict(xy=(.03, .03), text=r"AK4PFCHS", transform='axes', fontproperties=FONTPROPERTIES['small_bold']),
}

FIGURE_TEMPLATES = {

}

TASK_TEMPLATES = {

}
