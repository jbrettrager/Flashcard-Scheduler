# Flashcard Scheduler API

## Overview
This project implements a spaced repetition API for reviewing flashcards, built using the Django REST Framework.

## Initial Setup

This project uses Docker for containerized development and testing.  
Building the container automatically applies database migrations, and installs required modules.

```
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
    
    # As the above new_interval multiplies the previous interval by at least 1.5, 
    # it will never reduce in the instance of 2 correct answers back to back.
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
| Monotonicity                               | Subsequent correct answers must not shorten the previously scheduled interval                                  | Previous interval is multiplied by a multiplier which is guaranteed to be 1.5 or greater, insuring it cannot be reduced.           |

## Performance Notes
- **Algorithmic Efficiency:**
The new_due_date calculation runs in **O(1)** time per review as it only performs simple arithmetic operations after fetching the previous review record.
- **Database Efficiency:**
Retrieval of review results uses Django ORM queries that access only the necessary fields.
- **Scalability:**
Since each review update only touches one record (the reviewed card), the system scales linearly with the number of reviews. For larger datasets, additional optimizations (such as async background scheduling, use of a Redis database to cache due cards) could be introduced. 
- **I/O Considerations:**
The API Endpoints exchange compact JSON payloads - only essential fields are returned. This keeps the network overhead minimal.
- **Potential Optimizations:**
  - Caching of "due-cards" queries to reduce repetitive filtering.
  - Currently, **@transaction.atomic** is used to account for concurrent requests to counteract potential race conditions when writing to the database. If queries on this endpoint were to increase significantly, an asynchronous background task manager (such as Celery) could be implemented.
  - While the algorithm for new_due_date is O(1) complexity, the algorithm used by the /due-cards/ endpoint is O(n). In the event of a mass amount of cards being added to the system, the query could be optimized by the use of a subquery.
## Trade-off Discussion
  1. **Database Queries**
  - Chose a simple for loop approach to locate and iterate through all flashcards in the database to find corresponding user reviews. 
  - Trade-off: Easy to implement and easy to read, but introduces an N+1 query issue for larger datasets. Could optimize with the use of subqueries at the cost of more difficult to read code.
  2. **Timezone Handling**
  - Convert user timezone to UTC on retrieval.
  - Trade-off: Slight overhead, but ensures that all times in the database are uniformly UTC, while maintaining the ability to return timestamps in the user's timezone.
  3. **Code Complexity vs Maintainability**
  - Chose readability and simplicity over aggressively optimizing SQL queries. 
  - Trade-off: Minor performance costs, but makes it easier for future developers to understand and maintain the system.


## Technologies Used
- **Python 3.13**
- **Django 5 / Django REST Framework**
- **PostgreSQL 18**
- **Docker & docker-compose**

