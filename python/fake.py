import pandas as pd
from faker import Faker

# Create object
fake = Faker()

# Generate data
fake.name()
fake.text()
fake.address()
fake.email()
fake.date()
fake.country()
fake.phone_number()
fake.random_number(digits=5)

# Dataframe creation
fakeDataframe = pd.DataFrame({
 'date':[fake.date() for i in range(5)],
 #'text':[fake.text() for i in range(5)],
 'name':[fake.name() for i in range(5)],
 'email':[fake.email() for i in range(5)],
 'country':[fake.country() for i in range(5)],
 'address':[fake.address() for i in range(5)],
 'phone_number':[fake.phone_number() for i in range(5)]
 })
print(fakeDataframe)
