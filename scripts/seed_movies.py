import os
import sys
from pathlib import Path

import django

# Setup Django environment
# This script is located in /scripts/, so we need to add the parent directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils.text import slugify  # noqa: E402

from movies.models import Director, MysteryTitle, Series  # noqa: E402


def main():
    movies = [
        # --- Existing Seeds ---
        {
            "title": "Knives Out",
            "release_year": 2019,
            "director": "Rian Johnson",
            "description": "A detective investigates the death of a patriarch of an eccentric, combative family.",
            "series": "Benoit Blanc",
        },
        {
            "title": "Glass Onion",
            "release_year": 2022,
            "director": "Rian Johnson",
            "description": "Famed Southern detective Benoit Blanc travels to Greece for his latest case.",
            "series": "Benoit Blanc",
        },
        {
            "title": "Murder on the Orient Express",
            "release_year": 1974,
            "director": "Sidney Lumet",
            "description": "In December 1935, when his train is stopped by deep snow, Detective Hercule Poirot is called on to solve a murder that occurred in his car the night before.",
            "series": "Hercule Poirot (70s)",
        },
        {
            "title": "Death on the Nile",
            "release_year": 1978,
            "director": "John Guillermin",
            "description": "As Hercule Poirot enjoys a luxurious cruise down the Nile, a newlywed heiress is found murdered on board.",
            "series": "Hercule Poirot (70s)",
        },
        {
            "title": "Clue",
            "release_year": 1985,
            "director": "Jonathan Lynn",
            "description": "Six guests are anonymously invited to a strange mansion for dinner, but after their host is killed, they must cooperate with the staff to identify the murderer as the bodies pile up.",
        },
        {
            "title": "Gosford Park",
            "release_year": 2001,
            "director": "Robert Altman",
            "description": "Set in the 1930s, a group of pretentious rich and famous together with their servants gather for a shooting party at an English country house. A murder results in a investigation.",
        },
        {
            "title": "The Last of Sheila",
            "release_year": 1973,
            "director": "Herbert Ross",
            "description": "A year after his wife is killed by a hit-and-run driver, a game-playing movie producer invites a group of friends to spend a week on his yacht playing a scavenger hunt mystery game.",
        },
        {
            "title": "Sleuth",
            "release_year": 1972,
            "director": "Joseph L. Mankiewicz",
            "description": "A man who loves games and theater invites his wife's lover to his house for a battle of wits.",
        },
        {
            "title": "Rear Window",
            "release_year": 1954,
            "director": "Alfred Hitchcock",
            "description": "A photographer in a wheelchair spies on his neighbors from his Greenwich Village courtyard apartment window, and becomes convinced one of them has committed murder.",
        },
        {
            "title": "Dial M for Murder",
            "release_year": 1954,
            "director": "Alfred Hitchcock",
            "description": "A tennis player frames his unfaithful wife for first-degree murder after she inadvertently hinders his plan to kill her.",
        },
        {
            "title": "Vertigo",
            "release_year": 1958,
            "director": "Alfred Hitchcock",
            "description": "A former police detective juggles wrestling with his personal demons and becoming obsessed with a hauntingly beautiful woman.",
        },
        {
            "title": "Chinatown",
            "release_year": 1974,
            "director": "Roman Polanski",
            "description": "A private detective hired to expose an adulterer in 1930s Los Angeles finds himself caught up in a web of deceit, corruption, and murder.",
        },
        {
            "title": "L.A. Confidential",
            "release_year": 1997,
            "director": "Curtis Hanson",
            "description": "As corruption grows in 1950s Los Angeles, three policemen - one strait-laced, one brutal, and one sleazy - investigate a series of murders with their own brand of justice.",
        },
        {
            "title": "The Maltese Falcon",
            "release_year": 1941,
            "director": "John Huston",
            "description": "San Francisco private detective Sam Spade takes on a case that involves him with three eccentric criminals, a gorgeous liar, and their quest for a priceless statuette.",
        },
        {
            "title": "The Big Sleep",
            "release_year": 1946,
            "director": "Howard Hawks",
            "description": "Private detective Philip Marlowe is hired by a wealthy family. Before the complex case is over, he's seen murder, blackmail, and what might be love.",
        },
        {
            "title": "Witness for the Prosecution",
            "release_year": 1957,
            "director": "Billy Wilder",
            "description": "A veteran British barrister must defend his client in a murder trial that has surprise after surprise.",
        },
        {
            "title": "Anatomy of a Murder",
            "release_year": 1959,
            "director": "Otto Preminger",
            "description": "In a murder trial, the defendant says he suffered temporary insanity after the victim raped his wife. What is the truth, and will he win his case?",
        },
        {
            "title": "The Girl with the Dragon Tattoo",
            "release_year": 2011,
            "director": "David Fincher",
            "description": "Journalist Mikael Blomkvist is aided in his search for a woman who has been missing for forty years by Lisbeth Salander, a young computer hacker.",
        },
        {
            "title": "Gone Girl",
            "release_year": 2014,
            "director": "David Fincher",
            "description": "With his wife's disappearance having become the focus of an intense media circus, a man sees the spotlight turned on him when it's suspected that he may not be innocent.",
        },
        {
            "title": "Prisoners",
            "release_year": 2013,
            "director": "Denis Villeneuve",
            "description": "When Keller Dover's daughter and her friend go missing, he takes matters into his own hands as the police pursue multiple leads and the pressure mounts.",
        },
        # --- New Additions (Total 100) ---
        {
            "title": "Mystic River",
            "release_year": 2003,
            "director": "Clint Eastwood",
            "description": "The lives of three men who were childhood friends are shattered when one of them has a family tragedy.",
        },
        {
            "title": "The Fugitive",
            "release_year": 1993,
            "director": "Andrew Davis",
            "description": "Dr. Richard Kimble, unjustly accused of murdering his wife, must find the real killer while being the target of a nationwide manhunt led by a seasoned U.S. Marshal.",
        },
        {
            "title": "Zodiac",
            "release_year": 2007,
            "director": "David Fincher",
            "description": "Between 1968 and 1983, a San Francisco cartoonist becomes an amateur detective obsessed with tracking down the Zodiac Killer.",
        },
        {
            "title": "The Game",
            "release_year": 1997,
            "director": "David Fincher",
            "description": "After a wealthy San Francisco banker is given an opportunity to participate in a mysterious game, his life is turned upside down.",
        },
        {
            "title": "Gone Baby Gone",
            "release_year": 2007,
            "director": "Ben Affleck",
            "description": "Two Boston area detectives investigate a little girl's kidnapping, which ultimately turns into a crisis both professionally and personally.",
        },
        {
            "title": "Minority Report",
            "release_year": 2002,
            "director": "Steven Spielberg",
            "description": "In a future where a special police unit is able to arrest murderers before they commit their crimes, an officer from that unit is himself accused of a future murder.",
        },
        {
            "title": "Inside Man",
            "release_year": 2006,
            "director": "Spike Lee",
            "description": "A police detective, a bank robber, and a high-power broker enter high-stakes negotiations after the criminal's brilliant heist spirals into a hostage situation.",
        },
        {
            "title": "Sherlock Holmes",
            "release_year": 2009,
            "director": "Guy Ritchie",
            "description": "Detective Sherlock Holmes and his stalwart partner Watson engage in a battle of wits and brawn with a nemesis whose plot is a threat to all of England.",
        },
        {
            "title": "The Sixth Sense",
            "release_year": 1999,
            "director": "M. Night Shyamalan",
            "description": "A frightened, withdrawn Philadelphia boy who communicates with spirits seeks the help of a disheartened child psychologist.",
        },
        {
            "title": "Shutter Island",
            "release_year": 2010,
            "director": "Martin Scorsese",
            "description": "In 1954, a U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane.",
        },
        {
            "title": "M",
            "release_year": 1931,
            "director": "Fritz Lang",
            "description": "When the police in a German city are unable to catch a child-murderer, other criminals join in the manhunt.",
        },
        {
            "title": "North by Northwest",
            "release_year": 1959,
            "director": "Alfred Hitchcock",
            "description": "A New York City advertising executive goes on the run after being mistaken for a government agent by a group of foreign spies.",
        },
        {
            "title": "Citizen Kane",
            "release_year": 1941,
            "director": "Orson Welles",
            "description": "Following the death of publishing tycoon Charles Foster Kane, reporters scramble to uncover the meaning of his final utterance: 'Rosebud'.",
        },
        {
            "title": "Oldboy",
            "release_year": 2003,
            "director": "Park Chan-wook",
            "description": "After being kidnapped and imprisoned for fifteen years, Oh Dae-Su is released, only to find that he must find his captor in five days.",
        },
        {
            "title": "The Lives of Others",
            "release_year": 2006,
            "director": "Florian Henckel von Donnersmarck",
            "description": "In 1984 East Berlin, an agent of the secret police, conducting surveillance on a writer and his lover, finds himself becoming increasingly absorbed by their lives.",
        },
        {
            "title": "Memento",
            "release_year": 2000,
            "director": "Christopher Nolan",
            "description": "A man with short-term memory loss attempts to track down his wife's murderer.",
        },
        {
            "title": "Psycho",
            "release_year": 1960,
            "director": "Alfred Hitchcock",
            "description": "A Phoenix secretary embezzles $40,000 from her employer's client, goes on the run, and checks into a remote motel run by a young man under the domination of his mother.",
        },
        {
            "title": "The Usual Suspects",
            "release_year": 1995,
            "director": "Bryan Singer",
            "description": "A sole survivor tells of the twisty events leading up to a horrific gun battle on a boat, which began when five criminals met at a seemingly random police lineup.",
        },
        {
            "title": "The Prestige",
            "release_year": 2006,
            "director": "Christopher Nolan",
            "description": "After a tragic accident, two stage magicians engage in a battle to create the ultimate illusion while sacrificing everything they have to outwit each other.",
        },
        {
            "title": "Se7en",
            "release_year": 1995,
            "director": "David Fincher",
            "description": "Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his motives.",
        },
        {
            "title": "Parasite",
            "release_year": 2019,
            "director": "Bong Joon Ho",
            "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
        },
        {
            "title": "Mulholland Drive",
            "release_year": 2001,
            "director": "David Lynch",
            "description": "After a car wreck on the winding Mulholland Drive renders a woman amnesiac, she and a Hollywood-hopeful search for clues and answers across Los Angeles.",
        },
        {
            "title": "Blue Velvet",
            "release_year": 1986,
            "director": "David Lynch",
            "description": "The discovery of a severed human ear found in a field leads a young man on an investigation related to a beautiful, mysterious nightclub singer and a group of psychopathic criminals.",
        },
        {
            "title": "Rashomon",
            "release_year": 1950,
            "director": "Akira Kurosawa",
            "description": "The rape of a bride and the murder of her samurai husband are recalled from the perspectives of a bandit, the bride, the samurai's ghost and a woodcutter.",
        },
        {
            "title": "The Third Man",
            "release_year": 1949,
            "director": "Carol Reed",
            "description": "Pulp novelist Holly Martins travels to shadowy, postwar Vienna, only to find himself investigating the mysterious death of an old friend, Harry Lime.",
        },
        {
            "title": "Touch of Evil",
            "release_year": 1958,
            "director": "Orson Welles",
            "description": "A stark, perverse story of murder, kidnapping, and police corruption in a Mexican border town.",
        },
        {
            "title": "Double Indemnity",
            "release_year": 1944,
            "director": "Billy Wilder",
            "description": "An insurance representative lets himself be talked by a seductive housewife into a murder/insurance fraud scheme that arouses the suspicion of his insurance investigator.",
        },
        {
            "title": "Laura",
            "release_year": 1944,
            "director": "Otto Preminger",
            "description": "A police detective falls in love with the woman whose murder he is investigating.",
        },
        {
            "title": "Strangers on a Train",
            "release_year": 1951,
            "director": "Alfred Hitchcock",
            "description": "A psychotic socialite and a professional tennis star meet on a train and engage in a conversation about swapping murders.",
        },
        {
            "title": "The 39 Steps",
            "release_year": 1935,
            "director": "Alfred Hitchcock",
            "description": "A man in London tries to help a counter-espionage agent. But when the agent is killed and the man stands accused, he must go on the run to save himself and stop a spy ring.",
        },
        {
            "title": "The Lady Vanishes",
            "release_year": 1938,
            "director": "Alfred Hitchcock",
            "description": "While traveling in continental Europe, a rich young playgirl realizes that an elderly lady seems to have disappeared from the train.",
        },
        {
            "title": "Notorious",
            "release_year": 1946,
            "director": "Alfred Hitchcock",
            "description": "A woman is asked to spy on a group of Nazi friends in South America. How far will she have to go to ingratiate herself with them?",
        },
        {
            "title": "Rope",
            "release_year": 1948,
            "director": "Alfred Hitchcock",
            "description": "Two men attempt to prove they committed the perfect crime by hosting a dinner party close to the spot where they strangled their former classmate.",
        },
        {
            "title": "Primal Fear",
            "release_year": 1996,
            "director": "Gregory Hoblit",
            "description": "An altar boy is accused of murdering a priest, and the truth is buried deep beneath several layers of deception.",
        },
        {
            "title": "The Conversation",
            "release_year": 1974,
            "director": "Francis Ford Coppola",
            "description": "A paranoid, secretive surveillance expert has a crisis of conscience when he suspects that the couple he is spying on will be murdered.",
        },
        {
            "title": "Blow Out",
            "release_year": 1981,
            "director": "Brian De Palma",
            "description": "A movie sound recordist accidentally records the evidence that proves that a car accident was actually murder and consequently finds himself in danger.",
        },
        {
            "title": "Brick",
            "release_year": 2005,
            "director": "Rian Johnson",
            "description": "A teenage loner pushes his way into the underworld of a high school crime ring to investigate the disappearance of his ex-girlfriend.",
        },
        {
            "title": "Kiss Kiss Bang Bang",
            "release_year": 2005,
            "director": "Shane Black",
            "description": "A murder mystery brings together a private eye, a struggling actress, and a thief masquerading as an actor.",
        },
        {
            "title": "The Nice Guys",
            "release_year": 2016,
            "director": "Shane Black",
            "description": "In 1970s Los Angeles, a mismatched pair of private eyes investigate a missing girl and the mysterious death of a porn star.",
        },
        {
            "title": "Spotlight",
            "release_year": 2015,
            "director": "Tom McCarthy",
            "description": "The true story of how the Boston Globe uncovered the massive scandal of child molestation and cover-up within the local Catholic Archdiocese.",
        },
        {
            "title": "All the President's Men",
            "release_year": 1976,
            "director": "Alan J. Pakula",
            "description": "The Washington Post reporters Bob Woodward and Carl Bernstein uncover the details of the Watergate scandal that leads to President Nixon's resignation.",
        },
        {
            "title": "JFK",
            "release_year": 1991,
            "director": "Oliver Stone",
            "description": "New Orleans District Attorney Jim Garrison discovers there's more to the Kennedy assassination than the official story.",
        },
        {
            "title": "Searching",
            "release_year": 2018,
            "director": "Aneesh Chaganty",
            "description": "After his 16-year-old daughter goes missing, a desperate father breaks into her laptop to look for clues to find her.",
        },
        {
            "title": "A Simple Favor",
            "release_year": 2018,
            "director": "Paul Feig",
            "description": "Stephanie is a single mother with a parenting vlog who befriends Emily, a secretive upper-class woman who has a child at the same elementary school.",
        },
        {
            "title": "Game Night",
            "release_year": 2018,
            "directors": ["John Francis Daley", "Jonathan Goldstein"],
            "description": "A group of friends who meet regularly for game nights find themselves entangled in a real-life mystery when the brother of one of them is seemingly kidnapped by dangerous gangsters.",
        },
        {
            "title": "See How They Run",
            "release_year": 2022,
            "director": "Tom George",
            "description": "In the West End of 1950s London, plans for a movie version of a smash-hit play come to an abrupt halt after a pivotal member of the crew is murdered.",
        },
        {
            "title": "Bad Times at the El Royale",
            "release_year": 2018,
            "director": "Drew Goddard",
            "description": "Early 1970s. Four strangers check in at the El Royale Hotel. The hotel is deserted, staffed by a single desk clerk. Some of the new guests' reasons for being there are less than innocent.",
        },
        {
            "title": "Identity",
            "release_year": 2003,
            "director": "James Mangold",
            "description": "Stranded at a desolate Nevada motel during a nasty rainstorm, ten strangers become acquainted with each other when they realize that they're being killed off one by one.",
        },
        {
            "title": "The Hateful Eight",
            "release_year": 2015,
            "director": "Quentin Tarantino",
            "description": "In the dead of a Wyoming winter, a bounty hunter and his prisoner find shelter in a cabin currently inhabited by a collection of nefarious characters.",
        },
        {
            "title": "Reservoir Dogs",
            "release_year": 1992,
            "director": "Quentin Tarantino",
            "description": "When a simple jewelry heist goes horribly wrong, the surviving criminals begin to suspect that one of them is a police informant.",
        },
        {
            "title": "12 Monkeys",
            "release_year": 1995,
            "director": "Terry Gilliam",
            "description": "In a future world devastated by disease, a convict is sent back in time to gather information about the man-made virus that wiped out most of the human population.",
        },
        {
            "title": "Source Code",
            "release_year": 2011,
            "director": "Duncan Jones",
            "description": "A soldier wakes up in someone else's body and discovers he's part of an experimental government program to find the bomber of a commuter train in 8 minutes.",
        },
        {
            "title": "Moon",
            "release_year": 2009,
            "director": "Duncan Jones",
            "description": "Astronaut Sam Bell has a quintessentially personal encounter toward the end of his three-year stint on the Moon, where he, working alongside his computer, GERTY, sends back to Earth parcels of a resource that has helped diminish our planet's power problems.",
        },
        {
            "title": "Ex Machina",
            "release_year": 2014,
            "director": "Alex Garland",
            "description": "A young programmer is selected to participate in a ground-breaking experiment in synthetic intelligence by evaluating the human qualities of a highly advanced humanoid A.I.",
        },
        {
            "title": "Arrival",
            "release_year": 2016,
            "director": "Denis Villeneuve",
            "description": "A linguist works with the military to communicate with alien lifeforms after twelve mysterious spacecraft appear around the world.",
        },
        {
            "title": "Blade Runner 2049",
            "release_year": 2017,
            "director": "Denis Villeneuve",
            "description": "Young Blade Runner K's discovery of a long-buried secret leads him to track down former Blade Runner Rick Deckard, who's been missing for thirty years.",
        },
        {
            "title": "Incendies",
            "release_year": 2010,
            "director": "Denis Villeneuve",
            "description": "Twins journey to the Middle East to discover their family history and fulfill their mother's last wishes.",
        },
        {
            "title": "Enemy",
            "release_year": 2013,
            "director": "Denis Villeneuve",
            "description": "A man seeks out his exact look-alike after spotting him in a movie.",
        },
        {
            "title": "Sicario",
            "release_year": 2015,
            "director": "Denis Villeneuve",
            "description": "An idealistic FBI agent is enlisted by a government task force to aid in the escalating war against drugs at the border area between the U.S. and Mexico.",
        },
        {
            "title": "Wind River",
            "release_year": 2017,
            "director": "Taylor Sheridan",
            "description": "A veteran hunter helps an FBI agent investigate the murder of a young woman on a Wyoming Native American reservation.",
        },
        {
            "title": "Hell or High Water",
            "release_year": 2016,
            "director": "David Mackenzie",
            "description": "A divorced father and his ex-con older brother resort to a desperate scheme in order to save their family's ranch in West Texas.",
        },
        {
            "title": "No Country for Old Men",
            "release_year": 2007,
            "directors": ["Joel Coen", "Ethan Coen"],
            "description": "Violence and mayhem ensue after a hunter stumbles upon a drug deal gone wrong and more than two million dollars in cash near the Rio Grande.",
        },
        {
            "title": "Fargo",
            "release_year": 1996,
            "directors": ["Joel Coen", "Ethan Coen"],
            "description": "Jerry Lundegaard's inept crime falls apart due to his and his henchmen's bungling and the persistent police work of the pregnant Marge Gunderson.",
        },
        {
            "title": "The Big Lebowski",
            "release_year": 1998,
            "directors": ["Joel Coen", "Ethan Coen"],
            "description": "Jeff 'The Dude' Lebowski, mistaken for a millionaire of the same name, seeks restitution for his ruined rug and enlists his bowling buddies to help get it.",
        },
        {
            "title": "Blood Simple",
            "release_year": 1984,
            "directors": ["Joel Coen", "Ethan Coen"],
            "description": "The owner of a seedy small-town Texas bar discovers that one of his employees is having an affair with his wife. A chaotic chain of misunderstandings, lies and mischief ensues.",
        },
        {
            "title": "Miller's Crossing",
            "release_year": 1990,
            "directors": ["Joel Coen", "Ethan Coen"],
            "description": "Tom Reagan, an advisor to a Prohibition-era crime boss, tries to keep the peace between warring mobs but gets caught in the middle.",
        },
        {
            "title": "The Man Who Wasn't There",
            "release_year": 2001,
            "directors": ["Joel Coen", "Ethan Coen"],
            "description": "A laconic, chain-smoking barber creates a blackmail scheme to fund his entry into the dry-cleaning business.",
        },
        {
            "title": "Barton Fink",
            "release_year": 1991,
            "directors": ["Joel Coen", "Ethan Coen"],
            "description": "A renowned New York playwright is enticed to California to write for the movies and discovers the hellish truth of Hollywood.",
        },
        {
            "title": "Caché",
            "release_year": 2005,
            "director": "Michael Haneke",
            "description": "A married couple is terrorized by a series of surveillance tapes left on their front porch.",
        },
        {
            "title": "Burning",
            "release_year": 2018,
            "director": "Lee Chang-dong",
            "description": "Jong-su runs into a girl who used to live in the same neighborhood, who asks him to look after her cat while she's on a trip to Africa. When back, she introduces Ben, a mysterious guy she met there, who confesses his secret hobby.",
        },
        {
            "title": "The Handmaiden",
            "release_year": 2016,
            "director": "Park Chan-wook",
            "description": "A woman is hired as a handmaiden to a Japanese heiress, but secretly she is involved in a plot to defraud her.",
        },
        {
            "title": "Decision to Leave",
            "release_year": 2022,
            "director": "Park Chan-wook",
            "description": "A detective investigating a man's death in the mountains meets the dead man's mysterious wife in the course of his dogged sleuthing.",
        },
        {
            "title": "Memories of Murder",
            "release_year": 2003,
            "director": "Bong Joon Ho",
            "description": "In a small Korean province in 1986, two detectives struggle with the case of multiple young women being found raped and murdered by an unknown culprit.",
        },
        {
            "title": "Mother",
            "release_year": 2009,
            "director": "Bong Joon Ho",
            "description": "A mother desperately searches for the killer who framed her son for a girl's horrific murder.",
        },
        {
            "title": "The Chaser",
            "release_year": 2008,
            "director": "Na Hong-jin",
            "description": "A disgraced ex-policeman who runs a small ring of prostitutes finds himself in a race against time when one of his women goes missing.",
        },
        {
            "title": "The Wailing",
            "release_year": 2016,
            "director": "Na Hong-jin",
            "description": "Soon after a stranger arrives in a little village, a mysterious sickness starts spreading. A policeman, drawn into the incident, is forced to solve the mystery in order to save his daughter.",
        },
        {
            "title": "I Saw the Devil",
            "release_year": 2010,
            "director": "Kim Jee-woon",
            "description": "A secret agent exacts revenge on a serial killer through a series of captures and releases.",
        },
        {
            "title": "A Tale of Two Sisters",
            "release_year": 2003,
            "director": "Kim Jee-woon",
            "description": "A family is haunted by the tragedies of deaths within the family.",
        },
        {
            "title": "High and Low",
            "release_year": 1963,
            "director": "Akira Kurosawa",
            "description": "An executive of a shoe company becomes a victim of extortion when his chauffeur's son is kidnapped and held for a huge ransom.",
        },
        {
            "title": "Cure",
            "release_year": 1997,
            "director": "Kiyoshi Kurosawa",
            "description": "A wave of gruesome murders is sweeping Tokyo. The only connection is a bloody X carved into the neck of each victim. In each case, the murderer is found near the victim and remembers nothing of the crime.",
        },
    ]

    print(f"Seeding {len(movies)} mystery movies...")

    created_count = 0
    updated_count = 0

    for movie_data in movies:
        slug = slugify(f"{movie_data['title']} {movie_data['release_year']}")

        obj, created = MysteryTitle.objects.update_or_create(
            slug=slug,
            defaults={
                "title": movie_data["title"],
                "release_year": movie_data["release_year"],
                "description": movie_data["description"],
                "media_type": MysteryTitle.MediaType.MOVIE,
                # We leave user-voting fields (quality, difficulty) as defaults
                # We assume these are fair play candidates by default
                "is_fair_play_candidate": True,
            },
        )

        # Handle Directors
        directors_to_set = []

        # Helper function to get/create director
        def get_create_director(name):
            d_slug = slugify(name)
            director_obj, _ = Director.objects.get_or_create(
                slug=d_slug, defaults={"name": name}
            )
            return director_obj

        if "directors" in movie_data:
            for d_name in movie_data["directors"]:
                directors_to_set.append(get_create_director(d_name))
        elif "director" in movie_data:
            directors_to_set.append(get_create_director(movie_data["director"]))

        if directors_to_set:
            obj.directors.set(directors_to_set)

        # Handle Series
        series_name = movie_data.get("series")
        if series_name:
            series_slug = slugify(series_name)
            series, _ = Series.objects.get_or_create(
                slug=series_slug, defaults={"name": series_name}
            )
            obj.series = series
        else:
            # If a movie was previously in a series and now is not
            obj.series = None

        obj.save()

        if created:
            created_count += 1
            print(f"Created: {obj}")
        else:
            updated_count += 1
            print(f"Updated: {obj}")

    print(f"\nDone! Created {created_count} movies, updated {updated_count} movies.")


if __name__ == "__main__":
    main()
