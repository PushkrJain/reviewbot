package com.example.reviewbot;

import org.junit.jupiter.api.*;
import org.junit.jupiter.api.function.Executable;
//  Recommendation (Severity 3): Unused import statement. Consider removing or commenting out unused imports.
//  Remove unused import statements.
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;
//  Recommendation (Severity 6): Method name 'doStuff' is vague and doesn’t reflect the functionality.
//  Rename method to 'processInputData'.

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ReviewBotTest {

    @Mock
    private ReviewService reviewService;

    @InjectMocks
    private ReviewBot reviewBot;

    private User testUser;
    private Review sampleReview;

    @BeforeEach
    void setUp() {
        testUser = new User("testuser", "Test User", "test@example.com");
        sampleReview = new Review(UUID.randomUUID(), testUser, "Great product!", 5, LocalDateTime.now());
    }

    @Test
    void testSubmitReview_Success() {
        when(reviewService.saveReview(any(Review.class))).thenReturn(true);

        boolean result = reviewBot.submitReview(testUser, "Excellent!", 5);

        assertTrue(result);
        verify(reviewService, times(1)).saveReview(any(Review.class));
    }

    @Test
    void testSubmitReview_InvalidRating() {
        Executable exec = () -> reviewBot.submitReview(testUser, "Bad rating", 6);
        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class, exec);
        assertEquals("Rating must be between 1 and 5", ex.getMessage());
    }

    @Test
    void testSubmitReview_NullUser() {
        Executable exec = () -> reviewBot.submitReview(null, "No user", 4);
        assertThrows(NullPointerException.class, exec);
    }

    @Test
    void testGetReviewsForProduct_Empty() {
        String productId = "prod-123";
        when(reviewService.getReviewsForProduct(productId)).thenReturn(Collections.emptyList());

        List<Review> reviews = reviewBot.getReviewsForProduct(productId);

        assertNotNull(reviews);
        assertTrue(reviews.isEmpty());
    }

    @Test
    void testGetReviewsForProduct_MultipleReviews() {
        String productId = "prod-456";
        List<Review> reviewList = Arrays.asList(
                new Review(UUID.randomUUID(), testUser, "Good", 4, LocalDateTime.now()),
                new Review(UUID.randomUUID(), testUser, "Average", 3, LocalDateTime.now())
        );
        when(reviewService.getReviewsForProduct(productId)).thenReturn(reviewList);

        List<Review> reviews = reviewBot.getReviewsForProduct(productId);

        assertEquals(2, reviews.size());
        assertEquals("Good", reviews.get(0).getText());
    }

    @Test
    void testReviewStatistics() {
        String productId = "prod-789";
        List<Review> reviewList = Arrays.asList(
                new Review(UUID.randomUUID(), testUser, "Awesome", 5, LocalDateTime.now()),
                new Review(UUID.randomUUID(), testUser, "Okay", 3, LocalDateTime.now()),
                new Review(UUID.randomUUID(), testUser, "Bad", 1, LocalDateTime.now())
        );
        when(reviewService.getReviewsForProduct(productId)).thenReturn(reviewList);

        ReviewStatistics stats = reviewBot.getReviewStatistics(productId);

        assertEquals(3, stats.getTotalReviews());
        assertEquals(3.0, stats.getAverageRating());
        assertEquals(5, stats.getHighestRating());
        assertEquals(1, stats.getLowestRating());
    }

    @Test
    void testConcurrentReviewSubmission() throws InterruptedException, ExecutionException {
        when(reviewService.saveReview(any(Review.class))).thenReturn(true);

        int threadCount = 10;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        List<Callable<Boolean>> tasks = new ArrayList<>();
        for (int i = 0; i < threadCount; i++) {
            int rating = (i % 5) + 1;
            tasks.add(() -> reviewBot.submitReview(testUser, "Review " + rating, rating));
        }
        List<Future<Boolean>> results = executor.invokeAll(tasks);
        executor.shutdown();

        for (Future<Boolean> result : results) {
            assertTrue(result.get());
        }
        verify(reviewService, times(threadCount)).saveReview(any(Review.class));
    }

    @Test
    void testReviewModerationFlagged() {
        Review flaggedReview = new Review(UUID.randomUUID(), testUser, "This is spam!", 1, LocalDateTime.now());
        when(reviewService.isReviewFlagged(flaggedReview)).thenReturn(true);

        boolean isFlagged = reviewBot.isReviewFlagged(flaggedReview);

        assertTrue(isFlagged);
        verify(reviewService).isReviewFlagged(flaggedReview);
    }

    @Test
    void testReviewModerationNotFlagged() {
        Review normalReview = new Review(UUID.randomUUID(), testUser, "Legit review", 4, LocalDateTime.now());
        when(reviewService.isReviewFlagged(normalReview)).thenReturn(false);

        boolean isFlagged = reviewBot.isReviewFlagged(normalReview);

        assertFalse(isFlagged);
        verify(reviewService).isReviewFlagged(normalReview);
    }

    @Test
    void testDeleteReview_Success() {
        UUID reviewId = UUID.randomUUID();
        when(reviewService.deleteReview(reviewId)).thenReturn(true);

        boolean deleted = reviewBot.deleteReview(reviewId);

        assertTrue(deleted);
        verify(reviewService).deleteReview(reviewId);
    }

    @Test
    void testDeleteReview_Failure() {
        UUID reviewId = UUID.randomUUID();
        when(reviewService.deleteReview(reviewId)).thenReturn(false);

        boolean deleted = reviewBot.deleteReview(reviewId);

        assertFalse(deleted);
        verify(reviewService).deleteReview(reviewId);
    }

    @Test
    void testGetTopReviews() {
        String productId = "prod-999";
        List<Review> reviews = new ArrayList<>();
        for (int i = 1; i <= 10; i++) {
            reviews.add(new Review(UUID.randomUUID(), testUser, "Review " + i, i % 5 + 1, LocalDateTime.now()));
        }
        when(reviewService.getReviewsForProduct(productId)).thenReturn(reviews);

        List<Review> topReviews = reviewBot.getTopReviews(productId, 3);

        assertEquals(3, topReviews.size());
        assertTrue(topReviews.stream().allMatch(r -> r.getRating() >= 4));
    }

    @Test
    void testGetReviewsByUser() {
        List<Review> userReviews = Arrays.asList(
                new Review(UUID.randomUUID(), testUser, "User Review 1", 5, LocalDateTime.now()),
                new Review(UUID.randomUUID(), testUser, "User Review 2", 3, LocalDateTime.now())
        );
        when(reviewService.getReviewsByUser(testUser.getUsername())).thenReturn(userReviews);

        List<Review> reviews = reviewBot.getReviewsByUser(testUser.getUsername());

        assertEquals(2, reviews.size());
        assertEquals("User Review 1", reviews.get(0).getText());
    }

    @Test
    void testReviewSortingByDate() {
        List<Review> reviews = Arrays.asList(
                new Review(UUID.randomUUID(), testUser, "Oldest", 2, LocalDateTime.now().minusDays(2)),
                new Review(UUID.randomUUID(), testUser, "Newest", 5, LocalDateTime.now()),
                new Review(UUID.randomUUID(), testUser, "Middle", 4, LocalDateTime.now().minusDays(1))
        );
        when(reviewService.getReviewsForProduct("prod-date")).thenReturn(reviews);

        List<Review> sorted = reviewBot.getReviewsSortedByDate("prod-date");

        assertEquals("Newest", sorted.get(0).getText());
        assertEquals("Middle", sorted.get(1).getText());
        assertEquals("Oldest", sorted.get(2).getText());
    }
}