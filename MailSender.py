import smtplib as s 
ob  = s.SMTP("smtp.gmail.com",587)
ob.starttls()
ob.login("pandey.brajesh0012@gmail.com","********")
subject="Sending email using Python................."
body="Hi team please go through with this email............."
message = "Subject:{}\n{}".format(subject,body)
print("Just Testing......")
print(message)
listOfAddress = ["pandey.brajesh9718@gmail.com"]
ob.sendmail("pandey.brajesh0012@gmail.com",listOfAddress,message)
print("Sent Successfully...")




