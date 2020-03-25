import random
import sys

from discord.ext import commands
from discord.ext.commands import Bot
from discord import DMChannel


# Constants
prefix = "qc!"
swears = [
    "ya fool",
    "ya ass",
    "ya halfwit",
    "ya nincompoop",
    "ya dunce",
    "ya dolt",
    "ya ignoramus",
    "ya cretin",
    "ya imbecile",
    "ya moron",
    "ya simpleton",
    "ya dope",
    "ya ninny",
    "ya chump",
    "ya dimwit",
    "ya dumbo",
    "ya dum-dum",
    "ya dumb-bell",
    "ya loon",
    "ya jackass",
    "ya bonehead",
    "ya fathead",
    "ya numbskull",
    "ya blockhead",
    "ya knucklehead",
    "ya thickhead",
    "ya airhead",
    "ya pinhead",
    "ya birdbrain",
    "ya jerk",
    "ya donkey",
    "ya noodle",
    "ya twit",
    "ya git",
    "ya muppet",
    "ya schmuck",
    "ya dork",
    "ya dingbat",
    "ya wing-nut",
    "ya knobhead",
    "ya mofo",
    "ya arse",
    "chutiye",
    "bhosdike",
    "bhadwe",
    "madarchod",
    "behenchod"
]


# Also used for creating Yellow-text using Fix syntax
# highlighting in some places instead of manual string
# concatenation
async def create_error_message(message, swearing, plural=False):
    error = f"```fix\n{message}"
    if swearing:
        error += ", " + random.choice(swears)
    if plural:
        error += "s"
    error += ".```"

    return error


# Class Definitions
class Participant:
    """ Participant in the quiz.

    Mostly a bag of data.

    Attribute:
        id (int): unique id number given the to participant
        member (discord.user.User): object representing Discord member
        nick (str): nick of the participant for the quiz
        score (int): score of the participant for the quiz
    """

    def __init__(self, idt, member, nick, score=0):
        self.id = idt
        self.member = member
        self.nick = nick
        self.score = score


class QuizCommands:
    """ Class containing the list of commands that the bot offers.

    Contains a dictionary mapping the name to the usage, and
    help description.
    """

    # General Commands
    command_help = {
        "usage": "help",
        "desc": "display the help menu"}
    command_start_quiz = {
        "usage": "start_quiz quiz_name",
        "desc": "become the QM, and start a quiz with given name"}
    command_join = {
        "usage": "join nick",
        "desc": "join the quiz with chosen nick"}
    command_list = {
        "usage": "list",
        "desc": "view the members participating in the quiz"}
    command_scoreboard = {
        "usage": "scoreboard",
        "desc": "view the scoreboard for the quiz"}
    command_pass = {
        "usage": "pass",
        "desc": "pass your direct to the next participant"}
    command_remind = {
        "usage": "remind",
        "desc": "remind the current participant to answer the question"}
    command_pounce = {
        "usage": "pounce answer",
        "desc": "pounce on the current question with your answer on DM " +
                "to the bot"}
    command_swearing = {
        "usage": "swearing mode",
        "desc": "set swearing mode on (default) or off"}

    # QM Only Commands
    command_end_quiz = {
        "usage": "end_quiz",
        "desc": "end the quiz"}
    command_start_joining = {
        "usage": "start_joining",
        "desc": "start the joining period for the quiz"}
    command_end_joining = {
        "usage": "end_joining",
        "desc": "end the joining period for the quiz"}
    command_pounce_round = {
        "usage": "pounce_round direction",
        "desc": "start a pounce round in given direction (CW or ACW)"}
    command_direct = {
        "usage": "direct [team_number]",
        "desc": "give the next question with a chosen direct team (optional)"}
    command_start_pounce = {
        "usage": "start_pounce",
        "desc": "start pouncing period for the current question"}
    command_end_pounce = {
        "usage": "end_pounce",
        "desc": "end pouncing period for the current question"}
    command_bounce = {
        "usage": "bounce",
        "desc": "bounce the question to the next team"}
    command_score = {
        "usage": "score participant1 participant2... points",
        "desc": "give scores to the participants"}
    command_bounce_type = {
        "usage": "bounce_type type",
        "desc": "set bounce type bangalore (default) or normal"}


class QCBot(Bot):
    """ QuizClub bot for helping run pounce-n-bounce quizzes on a Discord
    server.

    Attributes:
        preix (str): prefix for the commands
        quiz_ongoing (bool): indicates whether a quiz is going on currently
        quiz_name (str): name of the quiz going on currently
        quizmaster (discord.user.User): User object of the person that is
            currently the quizmaster
        quizmaster_channel (discord.DMChannel): DMChannel of the current
            quizmaster
        question_ongoing (bool): indicates whether a question is going on
            currently
        participants ([Participant]): list of participants
        participating ({str: bool}): dictionary marking participating members
        no_of_participants (int): number of participants in the quiz
        pouncing_allowed (bool): indicates whether participants can pounce
        joining_allowed (bool): indicates whether new members can join
            the quiz
        direct_participant (int): no. of the participant that got the
            question as direct
        curr_participant (int): no. of the participant currently supposed
            to answer
        pounce_direction (str): CW or ACW represnging clockwise or
            anti-clockwise
        pounces ([Str]): list of pounces for the current question
        pounced ({str:}): dictionary indication which participants have
            pounced
        bounce_type (str): indicates type of bounce, bangalore (default)
            or normal
        swearing (bool): indicates whether the bot should swear or not
    """

    def __init__(self):
        super(QCBot, self).__init__(
            command_prefix=commands.when_mentioned_or(prefix))

        self.prefix = prefix
        self.quiz_ongoing = None
        self.quiz_name = None
        self.quizmaster = None
        self.quizmaster_channel = None
        self.question_ongoing = None
        self.participants = None
        self.participating = None
        self.no_of_participants = 0
        self.pouncing_allowed = None
        self.joining_allowed = None
        self.direct_participant = None
        self.curr_participant = None
        self.pounce_direction = None
        self.pounces = None
        self.pounced = None
        self.bounce_type = "bangalore"
        self.swearing = True

    def reset(self):
        self.quiz_ongoing = None
        self.quiz_name = None
        self.quizmaster = None
        self.quizmaster_channel = None
        self.question_ongoing = None
        self.participants = None
        self.participating = None
        self.no_of_participants = 0
        self.pouncing_allowed = None
        self.joining_allowed = None
        self.direct_participant = None
        self.curr_participant = None
        self.pounce_direction = None
        self.pounces = None
        self.pounced = None
        self.bounce_type = "bangalore"
        self.swearing = True


bot = QCBot()
bot.remove_command(name="help")


# Bot Commands
# General Commands
@bot.command(name="help")
async def command_help(ctx, *args):
    reply = "```fix\n"
    reply += "Help for the Quiz Club Bot.\n"
    reply += f"The prefix for this bot is - {bot.prefix}.\n\n"
    reply += "General Commands - \n\n"
    reply += (
        "\t" + QuizCommands.command_help["usage"] + " -\n\t\t" +
        QuizCommands.command_help["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_start_quiz["usage"] + " -\n\t\t" +
        QuizCommands.command_start_quiz["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_join["usage"] + " -\n\t\t" +
        QuizCommands.command_join["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_list["usage"] + " -\n\t\t" +
        QuizCommands.command_list["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_scoreboard["usage"] + " -\n\t\t" +
        QuizCommands.command_scoreboard["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_pass["usage"] + " -\n\t\t" +
        QuizCommands.command_pass["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_remind["usage"] + " -\n\t\t" +
        QuizCommands.command_remind["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_pounce["usage"] + " -\n\t\t" +
        QuizCommands.command_pounce["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_swearing["usage"] + " -\n\t\t" +
        QuizCommands.command_swearing["desc"] + "\n")
    reply += "\nQM Commands - \n\n"
    reply += (
        "\t" + QuizCommands.command_end_quiz["usage"] + " -\n\t\t" +
        QuizCommands.command_end_quiz["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_start_joining["usage"] + " -\n\t\t" +
        QuizCommands.command_start_joining["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_end_joining["usage"] + " -\n\t\t" +
        QuizCommands.command_end_joining["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_pounce_round["usage"] + " -\n\t\t" +
        QuizCommands.command_pounce_round["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_direct["usage"] + " -\n\t\t" +
        QuizCommands.command_direct["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_start_pounce["usage"] + " -\n\t\t" +
        QuizCommands.command_start_pounce["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_end_pounce["usage"] + " -\n\t\t" +
        QuizCommands.command_end_pounce["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_bounce["usage"] + " -\n\t\t" +
        QuizCommands.command_bounce["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_score["usage"] + " -\n\t\t" +
        QuizCommands.command_score["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_bounce_type["usage"] + " -\n\t\t" +
        QuizCommands.command_bounce_type["desc"] + "\n")
    reply += "```"

    await ctx.send(reply)


@bot.command(name="startQuiz")
async def start_quiz(ctx, *, quiz_name):
    if bot.quiz_ongoing:
        reply = await create_error_message(
            "There's already a quiz going on",
            bot.swearing
        )
        await ctx.send(reply)
        return

    bot.quiz_ongoing = True
    bot.quiz_name = quiz_name
    bot.quizmaster = ctx.author
    bot.quizmaster_channel = await bot.quizmaster.create_dm()
    bot.question_ongoing = False
    bot.participants = []
    bot.participating = {}
    bot.pouncing_allowed = False
    bot.joining_allowed = False
    bot.direct_participant = False
    bot.curr_participant = None
    bot.pounce_direction = "CW"
    bot.pounces = None
    bot.pounced = None
    bot.swearing = True

    reply = f"```fix\nStarting quiz - {quiz_name}.\n\n"
    reply += f"{bot.quizmaster} will be your QM for this quiz.```"

    await ctx.send(reply)


@bot.command(name="join")
async def join(ctx, nick, *args):
    # if ctx.author == bot.quizmaster:
    #     reply = await create_error_message(
    #         "QM cannot join the quiz",
    #         bot.swearing)
    #     await ctx.send(reply)
    #     return

    if not bot.quiz_ongoing:
        reply = await create_error_message(
            "There's no ongoing quiz",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if bot.participating.get(str(ctx.author)) is not None:
        reply = await create_error_message(
            "You are already participating",
            bot.swearing
        )
        await ctx.send(reply)
        return

    participant = Participant(
        bot.no_of_participants, ctx.author, nick)

    bot.participants.append(participant)
    bot.participating[str(ctx.author)] = bot.no_of_participants
    bot.no_of_participants += 1

    reply = "```fix\n"
    reply += "{} has joined the quiz as participant no. {}```".format(
        ctx.author,
        bot.no_of_participants
    )

    await ctx.send(reply)


@bot.command(name="list")
async def list_participants(ctx, *args):
    if not bot.quiz_ongoing:
        reply = await create_error_message(
            "There's no ongoing quiz",
            bot.swearing
        )
        await ctx.send(reply)
        return

    reply = f"```fix\nList of participants in {bot.quiz_name} - \n\n"

    for idx, participant in enumerate(bot.participants):
        reply += "\t{}. {} as {}".format(
            idx + 1,
            participant.member,
            participant.nick,
        )
        reply += "\n"

    reply += "```"
    await ctx.send(reply)


@bot.command(name="scoreboard")
async def scoreboard(ctx, *args):
    sorted_list = sorted(
        bot.participants, key=lambda item: item.score, reverse=True)

    reply = f"```fix\nCurrent Scoreboard for {bot.quiz_name} -"
    reply += "\n\n"

    for idx, participant in enumerate(sorted_list):
        reply += "\t{}. {} as {} - {} points".format(
            idx + 1,
            participant.member,
            participant.nick,
            participant.score
        )
        reply += "\n"

    reply += "```"
    await ctx.send(reply)


async def pounce_and_bounce_util(ctx, reply):
    while True:
        if bot.pounce_direction == "CW":
            bot.curr_participant = (
                (bot.curr_participant + 1) % bot.no_of_participants
            )
        else:
            bot.curr_participant = (
                (bot.curr_participant - 1) % bot.no_of_participants
            )

        if bot.curr_participant == bot.direct_participant:
            break

        participant = bot.participants[bot.curr_participant]
        if not bot.pounced.get(str(participant.member)):
            break
        else:
            reply += await create_error_message(
                f"{participant.member} [Number. {participant.id + 1}] "
                + "has pounced. moving on.\n",
                False
            )

    if bot.curr_participant == bot.direct_participant:
        reply += await create_error_message(
                "None of you got it",
                bot.swearing,
                True
        )

        if bot.bounce_type == "bangalore":
            bot.direct_participant = bot.direct_participant + 1

        await ctx.send(reply)
        return

    reply = f"{participant.member.mention}"
    reply += await create_error_message(
        f"[Number. {participant.id + 1}] -  It's your turn",
        bot.swearing
    )

    await ctx.send(reply)


@bot.command(name="pass")
async def pass_question(ctx, *args):
    if not bot.quiz_ongoing:
        reply = await create_error_message(
            "There's no ongoing quiz",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_error_message(
            "There's no ongoing question",
            bot.swearing
        )
        await ctx.send(reply)
        return

    participant = bot.participants[bot.curr_participant]
    if ctx.author != participant.member:
        reply = await create_error_message(
            "It's not your turn",
            bot.swearing
        )
        await ctx.send(reply)
        return

    reply = ctx.author.mention
    reply += await create_error_message(
        "Your turn is being passed over",
        False
    )

    await pounce_and_bounce_util(ctx, reply)


@bot.command(name="remind")
async def remind(ctx, *args):
    if not bot.quiz_ongoing:
        reply = await create_error_message(
            "There's no ongoing quiz",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_error_message(
            "There's no ongoing question",
            bot.swearing
        )
        await ctx.send(reply)
        return

    participant = bot.participants[bot.curr_participant]

    reply = f"{participant.member.mention}"
    reply += await create_error_message(
        f"[Number. {participant.id + 1}] -  It's your fucking turn",
        bot.swearing
    )

    await ctx.send(reply)


@bot.command(name="pounce")
async def pounce(ctx, *, answer):
    if not bot.quiz_ongoing:
        reply = await create_error_message(
            "There's no ongoing quiz",
            bot.swearing
        )
        await ctx.send(reply)
        return

    # if not bot.question_ongoing:
    #     reply = await create_error_message(
    #         "There's no ongoing question",
    #         bot.swearing
    #     )
    #     await ctx.send(reply)
    #     return

    idt = bot.participating.get(str(ctx.author))
    if idt is None:
        reply = await create_error_message(
            "You are not participating",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if not isinstance(ctx.message.channel, DMChannel):
        reply = await create_error_message(
            "Pounce on DM",
            bot.swearing)
        await ctx.send(reply)
        return

    participant = bot.participants[bot.curr_participant]
    if ctx.author == participant.member:
        reply = await create_error_message(
            "It's your direct",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if bot.pounced.get(str(ctx.author)):
        reply = await create_error_message(
            "You already pounced",
            bot.swearing
        )
        await ctx.send(reply)
        return

    bot.pounced[str(ctx.author)] = True
    pounce_answer = await create_error_message(
        f"[Number. {idt + 1}] -  {answer}",
        False
    )

    bot.pounces.append(pounce_answer)

    reply = await create_error_message(
        "You have pounced for this question with the answer - \n\n"
        + answer,
        False
    )

    await ctx.send(reply)


@bot.command(name="swearing")
async def swearing(ctx, mode, *args):
    if mode == "on":
        bot.swearing = True
    elif mode == "off":
        bot.swearing = False
    else:
        reply = await create_error_message(
            "Not a valid mode",
            bot.swearing
        )
        await ctx.send(reply)
        return

    reply = f"```fix\nSwearing has been turned {mode}.```"
    await ctx.send(reply)


@bot.command(name="endQuiz")
async def end_quiz(ctx, *args):
    if ctx.author != bot.quizmaster:
        reply = await create_error_message(
            "You are not the QM",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.quiz_ongoing:
        reply = await create_error_message(
            "There's no ongoing quiz",
            bot.swearing
        )
        await ctx.send(reply)
        return

    reply = f"```fix\nEnding quiz - {bot.quiz_name}.\n"
    reply += f"QM - {bot.quizmaster}.\n\n"
    reply += "Thank you for participating.\n\n"

    sorted_list = sorted(
        bot.participants, key=lambda item: item.score, reverse=True)

    reply += f"Final Scoreboard for {bot.quiz_name} -"
    reply += "\n\n"

    for idx, participant in enumerate(sorted_list):
        reply += "\t{}. {} as {} - {} points".format(
            idx + 1,
            participant.member,
            participant.nick,
            participant.score
        )
        reply += "\n"

    reply += "```"

    bot.reset()

    await ctx.send(reply)


@bot.command(name="bounce")
async def bounce(ctx, *args):
    if ctx.author != bot.quizmaster:
        reply = await create_error_message(
            "You are not the QM",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.quiz_ongoing:
        reply = await create_error_message(
            "There's no ongoing quiz",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_error_message(
            "There's no ongoing question",
            bot.swearing
        )
        await ctx.send(reply)
        return

    participant = bot.participants[bot.curr_participant]
    if ctx.author != participant.member:
        reply = await create_error_message(
            "It's not your turn",
            bot.swearing
        )
        await ctx.send(reply)
        return

    reply = ctx.author.mention
    reply += await create_error_message(
        "Question is begin bounced over",
        False
    )

    await pounce_and_bounce_util(ctx, reply)


@bot.command(name="bounceType")
async def bounce_type(ctx, bounce_type):
    if ctx.author != bot.quizmaster:
        reply = await create_error_message(
            "You are not the QM",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.quiz_ongoing:
        reply = await create_error_message(
            "There's no ongoing quiz",
            bot.swearing
        )
        await ctx.send(reply)
        return

    if bounce_type != "bangalore" and bounce_type != "normal":
        reply = await create_error_message(
            "Unknown bounce type",
            bot.swearing
        )
        await ctx.send(reply)
        return

    bot.bounce_type = bounce_type
    reply = await create_error_message(
        f"Bounce type changed to {bounce_type}",
        False
    )
    await ctx.send(reply)
    return


@bot.event
async def on_command_error(ctx, error):
    print(error, file=sys.stderr)
    reply = await create_error_message(
        "I am not really sure what you tried to do there.\n\n"
        + "Try viewing help",
        bot.swearing
    )

    await ctx.send(reply)


if __name__ == "__main__":
    bot.run("NjkxNzIzMDUzMTMwMDU1Nzkx.XnueVA.SbPT7fZSfyKMXHuUZyGFUMRNbPk")