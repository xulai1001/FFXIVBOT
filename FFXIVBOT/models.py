from django.db import models

# Create your models here.
class QQGroup(models.Model):
    group_id = models.CharField(primary_key=True,max_length=16)
    welcome_msg = models.TextField(default="",blank=True)
    repeat_ban = models.IntegerField(default=-1)
    repeat_length = models.IntegerField(default=-1)
    repeat_prob = models.IntegerField(default=0)
    left_reply_cnt = models.IntegerField(default=100)
    ban_cnt = models.IntegerField(default=-1)
    ban_till = models.BigIntegerField(default=0)

class CustomReply(models.Model):
	group = models.ForeignKey(QQGroup,on_delete=models.CASCADE)
	key = models.TextField(default="",blank=True)
	value = models.TextField(default="",blank=True)

class ChatMessage(models.Model):
	group = models.ForeignKey(QQGroup,on_delete=models.CASCADE)
	message = models.TextField(default="",blank=True)
	timestamp = models.BigIntegerField(default=0)
	times = models.IntegerField(default=1)
	repeated = models.BooleanField(default=False)

class Member(models.Model):
	user_id = models.CharField(max_length=16)
	group = models.ForeignKey(QQGroup,on_delete=models.CASCADE)
	ban_time = models.IntegerField(default=0)
	vote_list = models.TextField(default="{}")
	timestamp = models.BigIntegerField(default=0)

class Revenge(models.Model):
	user_id = models.CharField(max_length=16)
	group = models.ForeignKey(QQGroup,on_delete=models.CASCADE)
	vote_list = models.TextField(default="{}")
	timestamp = models.BigIntegerField(default=0)
	ban_time = models.IntegerField(default=0)


class Quest(models.Model):
	quest_id = models.IntegerField(primary_key=True)
	name = models.CharField(default="",max_length=64,blank=True)
	cn_name = models.CharField(default="",max_length=64,blank=True)
	def __str__(self):
		return str(self.name)

class Boss(models.Model):
	boss_id = models.IntegerField(primary_key=True)
	quest = models.ForeignKey(Quest,on_delete=models.CASCADE)
	name = models.CharField(default="",max_length=64,blank=True)
	cn_name = models.CharField(default="",max_length=64,blank=True)
	nickname = models.TextField(default="{}")
	add_time = models.BigIntegerField(default=0)
	cn_add_time = models.BigIntegerField(default=0)
	parsed_days = models.IntegerField(default=0)
	def __str__(self):
		return str(self.name)

class Job(models.Model):
	name = models.CharField(default="",max_length=64,blank=True)
	cn_name = models.CharField(default="",max_length=64,blank=True)
	nickname = models.TextField(default="{}")
	def __str__(self):
		return str(self.name)

class DPSTile(models.Model):
	boss = models.ForeignKey(Boss,on_delete=models.CASCADE)
	job = models.ForeignKey(Job,on_delete=models.CASCADE)
	day = models.IntegerField(default=0)
	attack = models.TextField(default="{}")
	class Meta:
		unique_together = ('boss', 'job', 'day',)
	def __str__(self):
		return str("%s_%s_%s_%s"%(self.boss,self.job,self.day))
		
class FFwall(models.Model):
	Id = models.TextField(primary_key=True)
	AreaId = models.IntegerField()
	AreaName = models.TextField()
	GroupId = models.IntegerField()
	GroupName = models.TextField()
	CharacterId = models.TextField()
	RoleId = models.IntegerField()
	RoleName = models.TextField()
	BigImage = models.TextField()
	SmallImage = models.TextField()
	uid = models.TextField()
	tags = models.TextField()
	
	def __str__(self):
		return str("%s_%s_%s_%s" % (self.Id, self.GroupName, self.CharacterId, self.RoleName))
		
class FFrecipe(models.Model):
	name = models.TextField(primary_key=True)
	recipe = models.TextField()
	
	def __str__(self):
		return str("%s_%s" % (self.name, self.recipe))

class YGOText(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    desc = models.TextField()
    class Meta:
        db_table = "texts"

class YGOData(models.Model):
    id = models.IntegerField(primary_key=True)
    atk = models.IntegerField()
    dfd = models.IntegerField(db_column="def")  # def is keyword, use dfd instead
    level = models.IntegerField()
    class Meta:
        db_table = "datas"

