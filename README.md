# Flashcard 

## Overview
This project implements a spaced repetition API for reviewing flashcards, built using the Django REST Framework.

## Algorithm Description
The review interval is determined by the user's rating after each review, as well as the interval given to the user from the previous review:
- The algorithm uses a Rating that is passed in the request body of the following format: 
- **Rating 0** -> Forgot
- **Rating 1** -> Remembered (with effort)
- **Rating 2** -> Instantly remembered

### Pseudocode
```
if {forgot}
    new_due_date = now + 1 minute
    
elif {first review}
    if {remembered}
        new_due_date = now + 5 days
    elif {instantly remembered}
        new_due_date = now + 15 days
        
else: 
    previous_interval = previous_due_date - previous_submit_date
    previous_interval_seconds = max(previous_interval.total_seconds(), 60)
    
    if {remembered}
        multiplier = 1.5
    elif {instantly remembered}
        multiplier = 2.5
    
    new_interval = previous_interval_seconds * multiplier
    next_due = now + new_interval
    
    # Monotonicity Check
    new_due_date = max(next_due, previous_due_date)
```

## Explanation
- If the user forgot the word -> The due date of the card is reset to the shortest interval of 1 minute.
- If this is the first time the user has reviewed this card -> base intervals are used (5 days if remembered with effort, 15 if remembered instantly)
- For subsequent reviews: The new interval scales based on performance
-- Rating 1 (Remembered with effort) -> interval * 1.5
-- Rating 2 (Instantly remembered) -> interval * 2.5
-- If rating 0 (forgot), the interval is reset to 1 minute.

## Why this algorithm satisfies Spacing Logic rules as described in the Notion page & Monotonicity
| Rule                                       | Description                                                                                                    | How this algorithm satisfies it                                                                                                    |
|--------------------------------------------|----------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| Increasing interval after remembering word | Each correct recall will increase the review interval by a multiplier that is greater than 1.                  | Remembered with effort results in a multiplier of 1.5, and instantly remember results in a multiplier of 2.5.                      |
| Reset after forgetting word                | Forgotten cards should be due again immediately after forgetting.                                              | A rating of 0 (forgot) resets interval to 1 minute.                                                                                |
| First Review special case                  | If the user instantly remembers (rating 2) on the first review, card must produce the longest initial interval | Algorithm checks if this is the first review, gives the longest initial interval (of 15 days) if instantly remembered (rating = 2) |
| Monotonicity                               | Subsequent correct answers must not shorten the previously scheduled interval                                  | Final monotonicity check in the algorithm ensures that the interval is not shortened.                                              |

## Initial Setup

This project uses Docker for containerized development and testing.  
Building the container automatically applies database migrations.

```bash
pip install -r requirements.txt
docker-compose build
```

### Run tests

```
docker-compose run --rm web python manage.py test
```

### Run server

```
docker-compose up
```

## Technologies Used
- **Python 3.13**
- **Django 5 / Django REST Framework**
- **PostgreSQL 18**
- **Docker & docker-compose**

