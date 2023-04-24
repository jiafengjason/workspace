from pytube import YouTube

link = input("Enter a youtube video's URL:") # i.e. https://youtu.be/dQw4w9WgXcQ

yt = YouTube(link)
print(yt.title)
print(yt.filename)
yt.streams.first().download()

print("downloaded", link)
