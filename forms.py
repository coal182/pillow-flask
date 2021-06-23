import glob
import os

from wtforms import Form, BooleanField, StringField, FloatField
from wtforms import SelectField, TextAreaField, validators

EXTENSION = '.png'


def get_basename(img):
    return os.path.splitext(os.path.basename(img))[0]


def get_logos(subdir='python'):
    logos = glob.glob(os.path.join('assets', subdir, '*' + EXTENSION))
    return [(logo, get_basename(logo)) for logo in logos]


DEFAULT_LOGOS = get_logos()


class ImageForm(Form):
    name = StringField('Banner Name', [

        validators.DataRequired(),
        validators.Length(max=100)
        ], 
        render_kw={'class': 'form-control'}
    )
    image_url1 = SelectField(
        'Pick a Logo',
        choices=DEFAULT_LOGOS, 
        render_kw={'class': 'form-select'}
    )
    image_url2 = StringField('Second Image URL', [
        validators.DataRequired(),
        validators.Length(max=500)
        ], 
        render_kw={'class': 'form-control'})
    text = TextAreaField('Text for Banner', [
        validators.DataRequired(),
        validators.Length(max=500), 
        ], 
        render_kw={'class': 'form-control'})
    price = StringField('Banner Price', [], render_kw={'class': 'form-control'})
    discount = StringField('Banner Discount', [], render_kw={'class': 'form-control'})
    background = StringField('Background', [], render_kw={'class': 'form-control'})
    background_transparency = BooleanField('Overlay?', default=False)
    remove_background = BooleanField('Remove BG?', default=False)
