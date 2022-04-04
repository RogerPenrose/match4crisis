"""
Add testing data to database.

route /accounts/add_data aufrufen um user zu generieren
muss in urls.py auskommentiert werden
"""
from django.core.management.base import BaseCommand, no_translations
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import numpy as np
from apps.accounts.models import User
from apps.offers.models import GenericOffer, AccommodationOffer, TransportationOffer, TranslationOffer, BuerocraticOffer, ManpowerOffer,ChildcareOfferShortterm, ChildcareOfferLongterm, WelfareOffer, JobOffer, DonationOffer



class Command(BaseCommand):
    help = "Populates the database with fake offers." 
    mail = lambda x: "%s@email.com" % x  # noqa: E731
   
    def add_arguments(self, parser):
    # Positional arguments
        parser.add_argument('n', type=int)
        parser.add_argument('--user_id', help="provide a user_id to be the author of all Offers, else the first available ID will be used", type=int)

    
    def handle(self, *args, **options):
        big_city_plzs = [
        "01067",
        "01069",
        "01097",
        "01099",
        "01109",
        "01127",
        "01129",
        "01139",
        "01157",
        "01159",
        "01169",
        "01187",
        "01189",
        "01217",
        "01219",
        "01237",
        "01239",
        "01257",
        "01259",
        "01277",
        "01279",
        "01307",
        "01309",
        "01324",
        "01326",
        "04103",
        "04105",
        "04107",
        "04109",
        "04129",
        "04155",
        "04157",
        "04158",
        "04159",
        "04177",
        "04178",
        "04179",
        "04205",
        "04207",
        "04209",
        "04229",
        "04249",
        "04275",
        "04277",
        "04279",
        "04288",
        "04289",
        "04299",
        "04315",
        "04316",
        "04317",
        "04318",
        "04328",
        "04329",
        "04347",
        "04349",
        "04356",
        "04357",
        "06108",
        "06110",
        "06112",
        "06114",
        "06116",
        "06118",
        "06120",
        "06122",
        "06124",
        "06126",
        "06128",
        "06130",
        "06132",
        "10115",
        "10117",
        "10119",
        "10178",
        "10179",
        "10243",
        "10245",
        "10247",
        "10249",
        "10315",
        "10317",
        "10318",
        "10319",
        "10365",
        "10367",
        "10369",
        "10405",
        "10407",
        "10409",
        "10435",
        "10437",
        "10439",
        "10551",
        "10553",
        "10555",
        "10557",
        "10559",
        "10585",
        "10587",
        "10589",
        "10623",
        "10625",
        "10627",
        "10629",
        "10707",
        "10709",
        "10711",
        "10713",
        "10715",
        "10717",
        "10719",
        "10777",
        "10779",
        "10781",
        "10783",
        "10785",
        "10787",
        "10789",
        "10823",
        "10825",
        "10827",
        "10829",
        "10961",
        "10963",
        "10965",
        "10967",
        "10969",
        "10997",
        "10999",
        "12043",
        "12045",
        "12047",
        "12049",
        "12051",
        "12053",
        "12055",
        "12057",
        "12059",
        "12099",
        "12101",
        "12103",
        "12105",
        "12107",
        "12109",
        "12157",
        "12159",
        "12161",
        "12163",
        "12165",
        "12167",
        "12169",
        "12203",
        "12205",
        "12207",
        "12209",
        "12247",
        "12249",
        "12277",
        "12279",
        "12305",
        "12307",
        "12309",
        "12347",
        "12349",
        "12351",
        "12353",
        "12355",
        "12357",
        "12359",
        "12435",
        "12437",
        "12439",
        "12459",
        "12487",
        "12489",
        "12524",
        "12526",
        "12527",
        "12529",
        "12555",
        "12557",
        "12559",
        "12587",
        "12589",
        "12619",
        "12621",
        "12623",
        "12625",
        "12627",
        "12629",
        "12679",
        "12681",
        "12683",
        "12685",
        "12687",
        "12689",
        "13051",
        "13053",
        "13055",
        "13057",
        "13059",
        "13086",
        "13088",
        "13089",
        "13125",
        "13127",
        "13129",
        "13156",
        "13158",
        "13159",
        "13187",
        "13189",
        "13347",
        "13349",
        "13351",
        "13353",
        "13355",
        "13357",
        "13359",
        "13403",
        "13405",
        "13407",
        "13409",
        "13435",
        "13437",
        "13439",
        "13465",
        "13467",
        "13469",
        "13503",
        "13505",
        "13507",
        "13509",
        "13581",
        "13583",
        "13585",
        "13587",
        "13589",
        "13591",
        "13593",
        "13595",
        "13597",
        "13599",
        "13627",
        "13629",
        "14050",
        "14052",
        "14053",
        "14055",
        "14057",
        "14059",
        "14089",
        "14109",
        "14129",
        "14163",
        "14165",
        "14167",
        "14169",
        "14193",
        "14195",
        "14197",
        "14199",
        "15230",
        "15232",
        "15234",
        "15236",
        "18055",
        "18057",
        "18059",
        "18069",
        "18106",
        "18107",
        "18109",
        "18119",
        "18146",
        "18147",
        "24937",
        "24939",
        "24941",
        "24943",
        "24944",
        "39104",
        "39106",
        "39108",
        "39110",
        "39112",
        "39114",
        "39116",
        "39118",
        "39120",
        "39122",
        "39124",
        "39126",
        "39128",
        "39130",
        "39221",
        "42103",
        "42105",
        "42107",
        "42109",
        "42111",
        "42113",
        "42115",
        "42117",
        "42119",
        "42275",
        "42277",
        "42279",
        "42281",
        "42283",
        "42285",
        "42287",
        "42289",
        "42327",
        "42329",
        "42349",
        "42369",
        "42389",
        "42399",
        "44135",
        "44137",
        "44139",
        "44141",
        "44143",
        "44145",
        "44147",
        "44149",
        "44225",
        "44227",
        "44229",
        "44263",
        "44265",
        "44267",
        "44269",
        "44287",
        "44289",
        "44309",
        "44319",
        "44328",
        "44329",
        "44339",
        "44357",
        "44359",
        "44369",
        "44379",
        "44388",
        "48143",
        "48145",
        "48147",
        "48149",
        "48151",
        "48153",
        "48155",
        "48157",
        "48159",
        "48161",
        "48163",
        "48165",
        "48167",
        "50667",
        "50668",
        "50670",
        "50672",
        "50674",
        "50676",
        "50677",
        "50678",
        "50679",
        "50733",
        "50735",
        "50737",
        "50739",
        "50765",
        "50767",
        "50769",
        "50823",
        "50825",
        "50827",
        "50829",
        "50858",
        "50859",
        "50931",
        "50933",
        "50935",
        "50937",
        "50939",
        "50968",
        "50969",
        "50996",
        "50997",
        "50999",
        "51061",
        "51063",
        "51065",
        "51067",
        "51069",
        "51103",
        "51105",
        "51107",
        "51109",
        "51143",
        "51145",
        "51147",
        "51149",
        "53111",
        "53113",
        "53115",
        "53117",
        "53119",
        "53121",
        "53123",
        "53125",
        "53127",
        "53129",
        "53173",
        "53175",
        "53177",
        "53179",
        "53225",
        "53227",
        "53229",
        "60385",
        "60386",
        "60388",
        "60435",
        "60437",
        "60438",
        "66111",
        "66113",
        "66115",
        "66117",
        "66119",
        "66121",
        "66123",
        "66125",
        "66126",
        "66127",
        "66128",
        "66129",
        "66130",
        "66131",
        "66132",
        "66133",
        "70173",
        "70174",
        "70176",
        "70178",
        "70180",
        "70182",
        "70184",
        "70186",
        "70188",
        "70190",
        "70191",
        "70192",
        "70193",
        "70195",
        "70197",
        "70199",
        "70327",
        "70329",
        "70372",
        "70374",
        "70376",
        "70378",
        "70435",
        "70437",
        "70439",
        "70469",
        "70499",
        "70563",
        "70565",
        "70567",
        "70569",
        "70597",
        "70599",
        "70619",
        "70629",
        "80331",
        "80333",
        "80335",
        "80336",
        "80337",
        "80339",
        "80469",
        "80538",
        "80539",
        "80634",
        "80636",
        "80637",
        "80638",
        "80639",
        "80686",
        "80687",
        "80689",
        "80796",
        "80797",
        "80798",
        "80799",
        "80801",
        "80802",
        "80803",
        "80804",
        "80805",
        "80807",
        "80809",
        "80933",
        "80935",
        "80937",
        "80939",
        "80992",
        "80993",
        "80995",
        "80997",
        "80999",
        "81241",
        "81243",
        "81245",
        "81247",
        "81249",
        "81369",
        "81371",
        "81373",
        "81375",
        "81377",
        "81379",
        "81475",
        "81476",
        "81477",
        "81479",
        "81539",
        "81541",
        "81543",
        "81545",
        "81547",
        "81549",
        "81667",
        "81669",
        "81671",
        "81673",
        "81675",
        "81677",
        "81679",
        "81735",
        "81737",
        "81739",
        "81825",
        "81827",
        "81829",
        "81925",
        "81927",
        "81929",
        ]
        JOB_CHOICES = ["ACA","ADM","ADV","CON","FAC","FIN","GEN","HEA", "HUM","INF","INT","LEG","LIB","MAR","OFF","PER","PUB","RES", "SPO", "STU","HAN"]
        residenceChoices = ['SO','RO', 'HO', 'LE'] 
        HELP_CHOICES_MP= ['ON',  'OS']
        GENDER_CHOICES = ['FE', 'MA', 'NO']
        HELP_CHOICES= ['AM', 'LE', 'OT']
        WELFARE_CHOICES = ["ELD", "DIS", "PSY"]
        user = User.objects.all()[0] 
        if options['user_id']:
            user_id = int(options["user_id"])
        if settings.DEBUG:
            n_offers = options["n"]
            plzs = np.random.choice(big_city_plzs, size=n_offers)
            counter = 0
            for i in range(n_offers):
                g = GenericOffer(
                    userId=user, \
                    created_at=timezone.now(), \
                    offerDescription="Automatically generated", \
                    isDigital=False,  \
                    country="DE", \
                    postCode=plzs[i], \
                    cost=0.00, \
                    active= (np.random.random() < 0.7), \
                    incomplete= (np.random.random() > 0.7),
                )
                
                if counter == 0: # Accommodation:

                    g.offerType = "AC"
                    g.save()
                    stayLength= np.random.randint(1, 365)
                    a = AccommodationOffer(genericOffer=g, \
                        numberOfAdults=np.random.randint(1, 15), \
                        numberOfChildren=np.random.randint(1, 3), \
                        numberOfPets=np.random.randint(0, 2), \
                        endDateAccommodation=timezone.now() + timedelta(days=stayLength) , \
                        typeOfResidence= residenceChoices[np.random.randint(0,len(residenceChoices)-1)] )     
                    a.save()
                if counter == 1: #Translation

                    g.offerType = "TL"
                    g.save()

                    t = TranslationOffer(genericOffer=g, \
                                firstLanguage="German", \
                                secondLanguage="English")
                    t.save()
                if counter == 2: # Accompaniment
                    g.offerType = "BU"
                    g.save()
                    b = BuerocraticOffer(genericOffer=g, helpType=HELP_CHOICES[np.random.randint(0,len(HELP_CHOICES)-1)])
                    b.save()
                if counter == 3: # Transportation

                    g.offerType = "TR"
                    g.save()
                    t = TransportationOffer(genericOffer=g, \
                        postCodeEnd=plzs[np.random.randint(0, n_offers)], \
                        numberOfPassengers=np.random.randint(0, 10))
                    t.save()
                if counter == 4: # Transportation

                    g.offerType = "MP"
                    g.save()
                    b = ManpowerOffer(genericOffer=g, helpType=HELP_CHOICES_MP[np.random.randint(0,len(HELP_CHOICES_MP)-1)])
                    b.save()
                if counter == 5: # Transportation
                    g.offerType = "CL"
                    g.save()
                    b = ChildcareOfferLongterm(genericOffer=g, gender=GENDER_CHOICES[np.random.randint(0,len(GENDER_CHOICES)-1)])
                    b.save()
                if counter == 6: # Transportation
                    g.offerType = "BA"
                    g.save()
                    b = ChildcareOfferShortterm(genericOffer=g, isRegular=(np.random.random() < 0.7),numberOfChildrenToCare=np.random.randint(0,5),gender=GENDER_CHOICES[np.random.randint(0,len(GENDER_CHOICES)-1)])
                    b.save()
                if counter == 7: # Transportation
                    g.offerType = "WE"
                    g.save()
                    b = WelfareOffer(genericOffer=g, helpType=WELFARE_CHOICES[np.random.randint(0,len(WELFARE_CHOICES)-1)])
                    b.save()
                if counter == 8: # Transportation
                    g.offerType = "JO"
                    g.save()
                    b = JobOffer(genericOffer=g, jobTitle="Master of awesome.", requirements="10 Year Job experience.", jobType=JOB_CHOICES[np.random.randint(0,len(JOB_CHOICES)-1)])
                    b.save()
                if counter == 9: # Transportation
                    g.offerType = "DO"
                    g.save()
                    b = DonationOffer(genericOffer=g, donationTitle="Human Fund", account="Deutsche Bank DE 12 3456 7891 07893.")
                    b.save()
                    counter = -1
                counter = counter + 1   
            return "Done. "+str(GenericOffer.objects.all().count())+" entries." 
        return ("Access forbidden: Not in debug mode.")