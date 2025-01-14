import logging
from email.policy import default
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active


class HostelRoom(models.Model):
    _name = "hostel.room"
    _description = "Hostel Room Information"
    _rec_name = "room_no"
    _inherit = ['base.archive']

    def _get_report_values(self, docids, data=None):
        docs = self.env['hostel.room'].browse(docids)
        return {
            'docs': docs,
        }

    name = fields.Char(string="Room Name", required=True)
    room_no = fields.Char("Room No.", required=True)
    floor_no = fields.Integer("Floor No.", default=1, help="Floor Number")
    currency_id = fields.Many2one('res.currency', string='Currency')
    rent_amount = fields.Monetary('Rent Amount', help="Enter rent amount per month")
    hostel_id = fields.Many2one("hostel.hostel", "hostel", help="Name of hostel")
    hostel_name = fields.Char(string="Hostel Name", related="hostel_id.name", store=True)
    active = fields.Boolean("Active", default=True,
                            help="Activate/Deactivate hostel record")
    member_ids = fields.Many2many('hostel.room.member', string='Members')
    student_ids = fields.One2many("hostel.student", "room_id",
                                  string="Students", help="Enter students")
    hostel_amenities_ids = fields.Many2many("hostel.amenities",
                                            "hostel_room_amenities_rel", "room_id", "amenitiy_id",
                                            string="Amenities", domain="[('active', '=', True)]",
                                            help="Select hostel room amenities")
    student_per_room = fields.Integer("Student Per Room", required=True,
                                      help="Students allocated per room")
    availability = fields.Float(compute="_compute_check_availability",
                                store=True, string="Availability", help="Room availability in hostel")
    state = fields.Selection([
        ('draft', 'Unavailable'),
        ('available', 'Available'),
        ('closed', 'Closed')],
        'State', default="draft")

    hostel_room_category_id = fields.Many2one(
        'hostel.room.category',
        string='Parent Category',
        ondelete='restrict',
        index=True
    )


    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'closed'),
                   ('closed', 'draft')]
        return (old_state, new_state) in allowed

    # in this method we use reporting error to user it is good developer practice
    def change_state(self, new_state):
        for room in self:
            if room.is_allowed_transition(room.state, new_state):
                room.state = new_state
            else:
                message = _('Moving from %s to %s is not allowed') % (room.state, new_state)
                raise UserError(message)

    def make_available(self):
        self.change_state('available')

    def make_closed(self):
        self.change_state('closed')

    _sql_constraints = [
        ("room_no_unique", "unique(room_no)", "Room number must be unique!")]

    # this is constraint to rise validation error
    @api.constrains("rent_amount")
    def _check_rent_amount(self):
        if self.rent_amount < 0:
            raise ValidationError(_("Rent Amount Per Month should not be a negative value!"))
    # check room availability
    @api.depends("student_per_room", "student_ids")
    def _compute_check_availability(self):
        for rec in self:
            rec.availability = abs(rec.student_per_room - len(rec.student_ids))

    # def log_all_room_members(self):
    #     hostel_room_obj = self.env['hostel.room.member']  # This is an empty recordset of model hostel.room.member
    #     all_members = hostel_room_obj.search([])
    #     print("ALL MEMBERS:", all_members)
    #     return True

    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }
        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }
        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        self.env['hostel.room.category'].create(parent_category_val)
        return True

    def update_room_no(self):
        self.ensure_one()
        self.room_no = self.room_no

    # def find_room(self):
    #     domain = [
    #         '|',
    #         '&', ('name', 'ilike', 'Room Name'),
    #         ('category_id.name', '=', 'Category Name'),
    #         '&', ('name', 'ilike', 'Second Room Name'),
    #         ('category_id.name', '=', 'Second Category Name')
    #     ]
    #     Rooms = self.search(domain)
    #     _logger.info('Room found: %s', Rooms)
    #     return True

        # Filter recordset

    def filter_members(self):
        all_rooms = self.search([])
        filtered_rooms = self.rooms_with_multiple_members(all_rooms)
        _logger.info('Filtered Rooms: %s', filtered_rooms)

    @api.model
    def rooms_with_multiple_members(self, all_rooms):
        def predicate(room):
            if len(room.member_ids) > 1:
                return True

        return all_rooms.filtered(predicate)

    # Traversing recordset
    def mapped_rooms(self):
        all_rooms = self.search([])
        room_authors = self.get_member_names(all_rooms)
        _logger.info('Rooms Members: %s', room_authors)

    @api.model
    def get_member_names(self, all_rooms):
        return all_rooms.mapped('member_ids.name')

    # Sorting recordset
    def sort_room(self):
        all_rooms = self.search([])
        rooms_sorted = self.sort_rooms_by_rating(all_rooms)
        _logger.info('Rooms before sorting: %s', all_rooms)
        _logger.info('Rooms after sorting: %s', rooms_sorted)

    @api.model
    def sort_rooms_by_rating(self, all_rooms):
        return all_rooms.sorted(key='room_rating')

class HostelRoomMember(models.Model):
    _name = 'hostel.room.member'
    _inherits = {'res.partner': 'partner_id'}
    _description = "Hostel Room member"

    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')
