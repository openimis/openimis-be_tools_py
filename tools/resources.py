from core import PATIENT_CATEGORY_MASK_MALE, PATIENT_CATEGORY_MASK_FEMALE, PATIENT_CATEGORY_MASK_ADULT, \
    PATIENT_CATEGORY_MASK_MINOR, filter_validity
from django.core.exceptions import ValidationError
from import_export import resources, fields
from import_export.fields import Field
from import_export.widgets import IntegerWidget, BooleanWidget

import medical.models
from medical.models import Item

# This class is responsible for customizing the import and export processes
class ItemResource(resources.ModelResource):
    user_id = -1  # used for the audit_user_id field

    # These 4 fields are columns added for the export
    # 'readonly=True' is supposed to ignore them during upload, but it doesn't seem to work
    male_cat = Field(readonly=True)
    female_cat = Field(readonly=True)
    adult_cat = Field(readonly=True)
    minor_cat = Field(readonly=True)

    # This field is added to signal that users might want to delete data during upload
    delete = Field(widget=BooleanWidget())

    def __init__(self, given_id):
        super().__init__()
        self.user_id = given_id

    class Meta:
        model = Item

        # These are the fields that are going to get exported/
        fields = ('code', 'name', 'type', 'package', 'price', 'quantity',
                  'care_type', 'frequency', 'patient_category')

        # You can customize the order for exports, but this order is also used during upload
        # (to know which fields will be there, instead of reading the headers)
        # export_order = ('code', 'name', 'type', 'package', 'price', 'quantity',
        #                 'care_type', 'frequency', 'male_cat', 'female_cat', 'adult_cat', 'minor_cat')

        # You can exclude some fields that will not be exported
        # exclude = ('validity_from', 'validity_to', 'legacy_id', 'id', 'uuid', 'audit_user_id', 'patient_category')
        exclude = ('patient_category',)

        # You can specify which column should be used for data ID during import (by default = 'id')
        import_id_fields = ('code',)

    # The 4 dehydrate_xxx_cat methods generate the data that is going to be put in the xxx_cat columns
    def dehydrate_male_cat(self, item):
        result = item.patient_category & PATIENT_CATEGORY_MASK_MALE
        return result if not result else 1

    def dehydrate_female_cat(self, item):
        result = item.patient_category & PATIENT_CATEGORY_MASK_FEMALE
        return result if not result else 1

    def dehydrate_adult_cat(self, item):
        result = item.patient_category & PATIENT_CATEGORY_MASK_ADULT
        return result if not result else 1

    def dehydrate_minor_cat(self, item):
        result = item.patient_category & PATIENT_CATEGORY_MASK_MINOR
        return result if not result else 1

    # This method is called once before importing data
    # This is used to add the two mandatory fields that are required for creating a medical.Item
    # If self.fields do not have a fields.Field, with the column_name set up, then these columns are ignored during import
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        if "patient_category" not in self.fields:
            self.fields["patient_category"] = fields.Field(attribute='patient_category', column_name="patient_category",
                                                           saves_null_values=False,
                                                           widget=IntegerWidget())
        if "audit_user_id" not in self.fields:
            self.fields["audit_user_id"] = fields.Field(attribute='audit_user_id', column_name="audit_user_id",
                                                        saves_null_values=False,
                                                        widget=IntegerWidget())

    # This method is called once for each row during import
    # This is where you can do some data validation/modification + add the missing data
    def before_import_row(self, row, **kwargs):
        # try:

        # Add here data validation for each field
        if row["type"] not in medical.models.Item.TYPE_VALUES:
            raise ValidationError("Invalid item type")

        # Transform the patient category data
        adult_cat = int(row["adult_cat"])
        minor_cat = int(row["minor_cat"])
        female_cat = int(row["female_cat"])
        male_cat = int(row["male_cat"])

        category = 0
        if male_cat:
            category = category | PATIENT_CATEGORY_MASK_MALE
        if female_cat:
            category = category | PATIENT_CATEGORY_MASK_FEMALE
        if adult_cat:
            category = category | PATIENT_CATEGORY_MASK_ADULT
        if minor_cat:
            category = category | PATIENT_CATEGORY_MASK_MINOR

        # Remove the now useless fields
        row.pop("adult_cat")
        row.pop("minor_cat")
        row.pop("female_cat")
        row.pop("male_cat")

        # Add the merged patient category value
        row["patient_category"] = category

        # Add missing user id data
        row["audit_user_id"] = self.user_id
        # except Exception as e:
        #     print(e)
        return row

    # This method can be overridden in order to define which data is valid during import.
    # For each row, the import process will try to find some matching data, then compare the data to the row,
    # then decide if the data must be updaded or if new data must be created.
    # As we save data history (with validity), the same code is used by many rows in the DB and
    # the plugin crashes when trying to fetch matching data
    def get_queryset(self):
        return Item.objects.filter(*filter_validity())

    # This method is called when the user flags a row to be deleted (the "delete" column value is '1')
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)


# If you want to have a custom column order, then there is a problem during import.
# In order to solve this, you can have a resource for exports and another one for imports.
# class ItemResourceImport(resources.ModelResource):
#     user_id = -1
#
#     def __init__(self, given_user_id):
#         super().__init__()
#         self.user_id = given_user_id
#
#     class Meta:
#         model = Item
#         export_order = ('code', 'name', 'type', 'package', 'price', 'quantity',
#                         'care_type', 'frequency', 'patient_category')
#         import_id_fields = ('code',)
#
#     def before_import_row(self, row, **kwargs):
#         try:
#             print("*** BEFORE ***")
#             print(row)
#             adult_cat = int(row["adult_cat"])
#             minor_cat = int(row["minor_cat"])
#             female_cat = int(row["female_cat"])
#             male_cat = int(row["male_cat"])
#
#             category = 0
#             if male_cat:
#                 category = category | PATIENT_CATEGORY_MASK_MALE
#             if female_cat:
#                 category = category | PATIENT_CATEGORY_MASK_FEMALE
#             if adult_cat:
#                 category = category | PATIENT_CATEGORY_MASK_ADULT
#             if minor_cat:
#                 category = category | PATIENT_CATEGORY_MASK_MINOR
#
#             row["patient_category"] = category
#             row["audit_user_id"] = self.user_id
#             row.pop("adult_cat")
#             row.pop("minor_cat")
#             row.pop("female_cat")
#             row.pop("male_cat")
#             print("*** AFTER ***")
#             print(row)
#         except Exception as e:
#             print(e)
#         return row
#