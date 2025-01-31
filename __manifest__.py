{
    "name": "Hostel Management",
    "summary": "Manage Hostel easily",
    "description": "Efficiently manage the entire residential facility in the school.",
    "version": "17.0.1.0.0",
    "author": "IdeaLogics",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": ["mail"],
    "data": [
        "security/hostel_security.xml",
        "security/ir.model.access.csv",
        "views/hostel.xml",
        "views/hostel_room.xml",
        'data/paperformat_data.xml',
        'reports/room_report_action.xml',
        'reports/hostel_room_report_template.xml',
        "views/hostel_room_category.xml",
        "views/hostel_amenities.xml",
        "views/hostel_student.xml",
        "views/hostel_categ.xml",
        "views/menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'my_hostel/static/src/css/custom_style.css',
        ],
    },
    "installable": True,
}
