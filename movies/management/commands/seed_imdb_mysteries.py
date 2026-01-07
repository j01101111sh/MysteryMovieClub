from django.core.management.base import BaseCommand
from django.utils.text import slugify

from movies.models import MysteryTitle


class Command(BaseCommand):
    help = "Seeds the database with 20 curated mystery movies from IMDb"

    def handle(self, *args, **kwargs):
        movies = [
            {
                "title": "Knives Out",
                "release_year": 2019,
                "director": "Rian Johnson",
                "description": "A detective investigates the death of a patriarch of an eccentric, combative family.",
            },
            {
                "title": "Glass Onion",
                "release_year": 2022,
                "director": "Rian Johnson",
                "description": "Famed Southern detective Benoit Blanc travels to Greece for his latest case.",
            },
            {
                "title": "Murder on the Orient Express",
                "release_year": 1974,
                "director": "Sidney Lumet",
                "description": "In December 1935, when his train is stopped by deep snow, Detective Hercule Poirot is called on to solve a murder that occurred in his car the night before.",
            },
            {
                "title": "Death on the Nile",
                "release_year": 1978,
                "director": "John Guillermin",
                "description": "As Hercule Poirot enjoys a luxurious cruise down the Nile, a newlywed heiress is found murdered on board.",
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
        ]

        self.stdout.write(f"Seeding {len(movies)} mystery movies...")

        created_count = 0
        updated_count = 0

        for movie_data in movies:
            slug = slugify(f"{movie_data['title']} {movie_data['release_year']}")

            obj, created = MysteryTitle.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": movie_data["title"],
                    "release_year": movie_data["release_year"],
                    "director": movie_data["director"],
                    "description": movie_data["description"],
                    "media_type": MysteryTitle.MediaType.MOVIE,
                    # We leave user-voting fields (quality, difficulty) as defaults
                    # We assume these are fair play candidates by default
                    "is_fair_play_candidate": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {obj}"))
            else:
                updated_count += 1
                self.stdout.write(f"Updated: {obj}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Created {created_count} movies, updated {updated_count} movies."
            )
        )
